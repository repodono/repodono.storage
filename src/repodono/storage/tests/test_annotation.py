# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAnnotatable
from zope.component import getGlobalSiteManager
from zope.component import adapter
from zope.component import getMultiAdapter
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


class IDummy4(Interface):
    readonly = schema.TextLine(title=u'Read Only Text', readonly=True)


@annotator(IDummy4)
class Dummy4(object):
    readonly = schema.fieldproperty.FieldProperty(IDummy4['readonly'])


class IDummy5(IDummy, IDummy4):
    pass


class Dummy5Base(object):
    def __init__(self):
        self.base = "This is a base dummy class"


@annotator(IDummy5)
class Dummy5Init1(Dummy5Base):

    def __init__(self):
        # This will not work because the class annotations can mess with
        # inheritance and this particular one __really__ mess everything
        # up.  If the following super call is needed, the first argument
        # must be the class before it got decorated with.

        # super(Dummy5Init1, self).__init__()

        # So, do this instead.
        Dummy5Base.__init__(self)
        self.calc = "Some calculated value"


@adapter(IAnnotatable, Interface, Interface)
@annotator(IDummy5)
class Dummy5Init2(Dummy5Base):
    def __init__(self, arg1, arg2):
        Dummy5Base.__init__(self)
        self.calc = arg1 + arg2


class AnnotationTestCase(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory=Dummy)
        gsm.registerAdapter(factory=Dummy2)
        gsm.registerAdapter(factory=Dummy3)
        gsm.registerAdapter(factory=Dummy4)
        gsm.registerAdapter(factory=Dummy5Init1)
        gsm.registerAdapter(factory=Dummy5Init2)

    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(factory=Dummy)
        gsm.unregisterAdapter(factory=Dummy2)
        gsm.unregisterAdapter(factory=Dummy3)
        gsm.unregisterAdapter(factory=Dummy4)
        gsm.unregisterAdapter(factory=Dummy5Init1)
        gsm.unregisterAdapter(factory=Dummy5Init2)

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
        with self.assertRaises(schema.interfaces.RequiredMissing):
            dummy.field1 = None
        with self.assertRaises(schema.interfaces.WrongType):
            dummy.field3 = u'test'

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

    def test_annotation_readonly_fields(self):
        dummy = IDummy4(self.portal)
        # Initial assignment should work
        dummy.readonly = u'Value to be frozen.'

        with self.assertRaises(ValueError) as cm:
            dummy.readonly = u"Can't assign this"

        self.assertEqual(cm.exception.args, ('readonly', 'field is readonly'))

        # underlying mapping is not manipulated beyond that.
        annotations = IAnnotations(self.portal)
        value = annotations['repodono.storage.tests.test_annotation.Dummy4']
        self.assertEqual(value['readonly'], u'Value to be frozen.')

        # forced manipulation
        value['readonly'] = u'Forced manipulation'
        dummy = IDummy4(self.portal)
        self.assertEqual(dummy.readonly, u'Forced manipulation')

    def test_annotation_init_method_standard(self):
        dummy = IDummy5(self.portal)
        # Initial assignment should work
        self.assertEqual(dummy.calc, "Some calculated value")
        self.assertEqual(dummy.base, "This is a base dummy class")

    def test_annotation_init_method_standard_multi_arg(self):
        # TODO add following to documentation to usage

        # Note how the __init__ method in the concrete implementation
        # above (in class Dummy5Init2) the arguments do not contain a
        # context, but this accepts it.  Reason is how the decorator
        # injected that argument into the method then consume it at the
        # end before passing it back to the decoratee class's __init__
        # method.  However note that super().__init__ cannot be called
        # for multiple reasons, including the mismatch of arguments.
        # This may be fixed later, but for now accept the weirdness in
        # the number of arguments.

        dummy = Dummy5Init2(self.portal, 'testv1', 'testv2')
        self.assertEqual(dummy.calc, "testv1testv2")
        self.assertEqual(dummy.base, "This is a base dummy class")

        # Should work through ZCA.
        dummy = getMultiAdapter((self.portal, 'testv1', 'testv2'), IDummy5)
        self.assertEqual(dummy.calc, "testv1testv2")
        self.assertEqual(dummy.base, "This is a base dummy class")
