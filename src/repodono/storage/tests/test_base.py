# -*- coding: utf-8 -*-
from zope.interface import alsoProvides
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.annotation.interfaces import IAnnotations
from repodono.storage.interfaces import IStorageBackend
from repodono.storage.interfaces import IStorageEnabled
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.interfaces import IStorageInfo
from repodono.storage.base import BaseStorageBackend

from plone.app.contenttypes.tests.robot.variables import TEST_FOLDER_ID

from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing import storage

import unittest


class BaseDefaultTestCase(unittest.TestCase):

    def test_default_impl(self):
        # default data, no annotation
        backend = BaseStorageBackend()
        self.assertRaises(NotImplementedError, backend.acquire, None)
        self.assertRaises(NotImplementedError, backend.install, None)


class StorageFactoryTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)

    def test_not_enabled_fail(self):
        with self.assertRaises(TypeError):
            IStorageFactory(self.folder)

    def test_default_impl_no_backend(self):
        alsoProvides(self.folder, IStorageEnabled)
        sf = IStorageFactory(self.folder)
        with self.assertRaises(ConstraintNotSatisfied):
            sf.backend = u'test'


class StorageFactoryRegisteredTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        # Register a dummy backend
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)
        self.backend = storage.DummyStorageBackend()
        self.portal.getSiteManager().registerUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_a')
        self.portal.getSiteManager().registerUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_b')

    def tearDown(self):
        self.portal.getSiteManager().unregisterUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_a')
        self.portal.getSiteManager().unregisterUtility(
            self.backend, provided=IStorageBackend, name=u'dummy_b')

    def test_default_impl_readonly(self):
        alsoProvides(self.folder, IStorageEnabled)
        sf = IStorageFactory(self.folder)
        sf.backend = u'dummy_a'
        self.assertEqual(sf.backend, u'dummy_a')

        with self.assertRaises(ValueError) as cm:
            sf.backend = u'dummy_b'

        self.assertEqual(cm.exception.args, ('backend', 'field is readonly'))


class StorageInfoTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)

    def test_storage_info_annotation_success(self):
        # default data, no annotation
        storage_info = IStorageInfo(self.folder)
        self.assertIsNone(storage_info.path)
        storage_info.path = u'Some Path'

        self.assertIn(
            'repodono.storage.base.StorageInfo',
            IAnnotations(self.folder).keys())
