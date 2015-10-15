# -*- coding: utf-8 -*-
from zope.annotation.interfaces import IAnnotations

from repodono.storage.interfaces import IStorageInfo
from repodono.storage.base import BaseStorageBackend

from plone.app.contenttypes.tests.robot.variables import TEST_FOLDER_ID

from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING

import unittest


class StorageInfoTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)

    def test_default_impl(self):
        # default data, no annotation
        backend = BaseStorageBackend()
        self.assertRaises(NotImplementedError, backend.acquire, None)
        self.assertRaises(NotImplementedError, backend.install, None)

    def test_storage_info_annotation_success(self):
        # default data, no annotation
        storage_info = IStorageInfo(self.folder)
        self.assertIsNone(storage_info.path)
        storage_info.path = u'Some Path'

        self.assertIn(
            'repodono.storage.base.StorageInfo',
            IAnnotations(self.folder).keys())
