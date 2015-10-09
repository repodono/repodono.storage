# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getGlobalSiteManager
from persistent.dict import PersistentDict

from repodono.storage.annotation import factory

from plone.app.testing import PLONE_INTEGRATION_TESTING

import unittest


class IDummy(Interface):

    field1 = schema.TextLine(title=u'field1')
    field2 = schema.TextLine(title=u'field2')


@factory(IDummy)
class Dummy(object):
    pass


class AnnotationTestCase(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory=Dummy)

    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(factory=Dummy)

    def test_annotation_fail(self):
        self.assertRaises(TypeError, IDummy, self.portal)

    def test_annotation_standard_lifecycle(self):
        Dummy.install(self.portal)
        dummy = IDummy(self.portal)
        self.assertIsNone(dummy.field1)
        self.assertIsNone(dummy.field2)

        annotations = IAnnotations(self.portal)
        self.assertIn('repodono.storage.tests.test_annotation.Dummy',
            annotations.keys())

        a = annotations['repodono.storage.tests.test_annotation.Dummy']
        self.assertTrue(isinstance(a, PersistentDict))

        Dummy.uninstall(self.portal)
        self.assertNotIn('repodono.storage.tests.test_annotation.Dummy',
            annotations.keys())
