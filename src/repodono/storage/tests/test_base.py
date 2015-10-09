# -*- coding: utf-8 -*-
from zope.annotation.interfaces import IAnnotations

from repodono.storage.interfaces import IStorageInfo
from repodono.storage.base import StorageInfo

from plone.app.contenttypes.tests.robot.variables import TEST_FOLDER_ID

from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING

import unittest


class StorageInfoTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal.get(TEST_FOLDER_ID)

    def test_storage_info_annotation_fail(self):
        # default data, no annotation
        self.assertRaises(TypeError, IStorageInfo, self.folder)

    def test_storage_info_annotation_success(self):
        # default data, no annotation
        StorageInfo.install(self.folder)
        storage_info = IStorageInfo(self.folder)
        self.assertIsNone(storage_info.path)

        self.assertIn('repodono.storage.base.StorageInfo',
            IAnnotations(self.folder).keys())
