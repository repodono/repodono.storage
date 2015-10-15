# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getGlobalSiteManager
from persistent.mapping import PersistentMapping

from repodono.storage.annotation import annotator
from repodono.storage.annotation import to_key

from plone.app.testing import PLONE_INTEGRATION_TESTING

import unittest


class IDummy(Interface):
    field1 = schema.TextLine(title=u'field1')
    field2 = schema.TextLine(title=u'field2', default=u'Test')


@annotator(IDummy)
class Dummy(object):
    pass


class IDummy2(IDummy):
    field3 = schema.Int(title=u'field3')


@annotator(IDummy2)
class Dummy2(object):
    field1 = schema.fieldproperty.FieldProperty(IDummy2['field1'])
    field3 = schema.fieldproperty.FieldProperty(IDummy2['field3'])


class IDummy3(IDummy):
    def foo():
        pass


@annotator(IDummy3)
class Dummy3(object):
    field2 = schema.fieldproperty.FieldProperty(IDummy3['field2'])

    def foo(self):
        pass


class AnnotationTestCase(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory=Dummy)
        gsm.registerAdapter(factory=Dummy2)
        gsm.registerAdapter(factory=Dummy3)

    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(factory=Dummy)
        gsm.unregisterAdapter(factory=Dummy2)
        gsm.unregisterAdapter(factory=Dummy3)

    def test_annotation_fail(self):
        # Fail on mismatched type in annotation.
        annotations = IAnnotations(self.portal)
        annotations['repodono.storage.tests.test_annotation.Dummy'] = object()
        self.assertRaises(TypeError, IDummy, self.portal)

    def test_annotation_classdef(self):
        self.assertEqual(Dummy.__name__, 'Dummy')
        self.assertEqual(
            Dummy.__module__, 'repodono.storage.tests.test_annotation')

    def test_annotation_basic_standard_lifecycle(self):
        # life cycle for a standard item.
        annotations = IAnnotations(self.portal)
        dummy = IDummy(self.portal)
        self.assertIsNone(dummy.field1)
        self.assertIsNone(dummy.field2)

        annotations = IAnnotations(self.portal)
        self.assertNotIn(
            'repodono.storage.tests.test_annotation.Dummy',
            annotations.keys())

        # assign some values
        dummy.field1 = u'Test'

        # Now the annotation will be in assigned.
        value = annotations['repodono.storage.tests.test_annotation.Dummy']
        self.assertTrue(isinstance(value, PersistentMapping))
        self.assertEqual(value, {'field1': u'Test'})

        # assign more values.
        dummy.field2 = 1
        dummy.field3 = 1

        # only fields defined in the interface are persisted.
        self.assertEqual(value, {'field1': u'Test', 'field2': 1})

        old = dummy.uninstall()
        self.assertNotIn(
            'repodono.storage.tests.test_annotation.Dummy',
            annotations.keys())
        self.assertFalse(isinstance(old, PersistentMapping))
        self.assertEqual(old, {'field1': u'Test', 'field2': 1})

    def test_annotation_not_field_no_mapping(self):
        # Assignment of unrelated fields will not trigger addition of
        # mapping
        dummy = IDummy3(self.portal)
        dummy.not_schema = u'Some value'
        # Failed assignments will not trigger addition of mapping.
        annotations = IAnnotations(self.portal)
        self.assertNotIn(
            'repodono.storage.tests.test_annotation.Dummy2',
            annotations.keys())

        # Likewise with a method defined in schema interface.
        dummy.foo = u'Some value'
        # Failed assignments will not trigger addition of mapping.
        annotations = IAnnotations(self.portal)
        self.assertNotIn(
            'repodono.storage.tests.test_annotation.Dummy2',
            annotations.keys())

    def test_annotation_schema_fail_no_mapping(self):
        dummy = IDummy2(self.portal)
        # standard schema validation kicks in
        self.assertRaises(
            schema.interfaces.RequiredMissing,
            setattr, dummy, 'field1', None)
        self.assertRaises(
            schema.interfaces.WrongType,
            setattr, dummy, 'field3', u'test')

        # No mapping persisted.
        annotations = IAnnotations(self.portal)
        self.assertNotIn(
            'repodono.storage.tests.test_annotation.Dummy2',
            annotations.keys())

    def test_annotation_schema_standard_lifecycle(self):
        dummy = IDummy2(self.portal)

        self.assertIsNone(dummy.field1)
        self.assertIsNone(dummy.field2)
        self.assertIsNone(dummy.field3)

        # Failed assignments will not trigger addition of mapping.
        annotations = IAnnotations(self.portal)
        self.assertNotIn(
            'repodono.storage.tests.test_annotation.Dummy2',
            annotations.keys())

        # assign some values
        dummy.field1 = u'Test'
        dummy.field2 = u'Value'
        dummy.field3 = 1

        annotations = IAnnotations(self.portal)
        value = annotations['repodono.storage.tests.test_annotation.Dummy2']
        self.assertEqual(
            value, {'field1': u'Test', 'field2': u'Value', 'field3': 1})

        dummy.uninstall()
        self.assertNotIn(
            'repodono.storage.tests.test_annotation.Dummy2',
            annotations.keys())

    def test_annotation_schema_direct_mapping_manipulation(self):
        dummy = IDummy2(self.portal)
        annotations = IAnnotations(self.portal)
        d = annotations[
            'repodono.storage.tests.test_annotation.Dummy2'
            ] = PersistentMapping()
        d['field1'] = u'Test'
        d['field3'] = 2

        # Unaffected as attribute access doesn't hit the mapping.
        self.assertIsNone(dummy.field1)
        self.assertIsNone(dummy.field3)

        dummy = IDummy2(self.portal)
        self.assertEqual(dummy.field1, u'Test')
        self.assertEqual(dummy.field3, 2)

    def test_annotation_schema_ignore_methods(self):
        # apply to mapping to annotation
        IDummy3(self.portal).field1 = None

        # force an attribute that maps to a method into mapping
        annotations = IAnnotations(self.portal)
        value = annotations['repodono.storage.tests.test_annotation.Dummy3']
        value['foo'] = 'bar'
        dummy = IDummy3(self.portal)

        # Method is not turned into attribute
        self.assertIsNone(dummy.field1)
        self.assertEqual(dummy.field2, 'Test')
        self.assertTrue(callable(dummy.foo))

        # Overriding a method to a value should not modify underlying
        # mapping
        dummy.foo = 1
        self.assertEqual(value, {'foo': 'bar', 'field1': None})

    def test_annotation_source_schema_violation_recovery(self):
        dummy = IDummy3(self.portal)
        dummy.field2 = u'A valid value'

        annotations = IAnnotations(self.portal)
        value = annotations['repodono.storage.tests.test_annotation.Dummy3']
        value['field2'] = 222
        self.assertRaises(TypeError, IDummy3, self.portal)

        # can still extract with a bare alternative class that isn't
        # registered in ZCA but references the correct call

        @annotator(IDummy3, to_key(__name__, 'Dummy3'))
        class Dummy3alt(object):
            pass

        dummy = Dummy3alt(self.portal)
        self.assertEqual(dummy.field2, 222)
