# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import os
from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING
from zope.component import getUtility
from plone import api
from plone.registry.interfaces import IRegistry

import unittest


class TestSetup(unittest.TestCase):
    """Test that repodono.storage is properly installed."""

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if repodono.storage is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('repodono.storage'))

    def test_browserlayer(self):
        """Test that IRepodonoStorageLayer is registered."""
        from repodono.storage.interfaces import IRepodonoStorageLayer
        from plone.browserlayer import utils
        self.assertIn(IRepodonoStorageLayer, utils.registered_layers())

    def test_registery_backend_root(self):
        """Test the backend_root registry settings."""
        registry = getUtility(IRegistry)
        self.assertEqual(
            registry['repodono.storage.backend_root'],
            os.environ['CLIENT_HOME'],
        )
        # Modification.
        registry['repodono.storage.backend_root'] = u'/tmp'
        # Add-on reinstallation should not overwrite existing value.
        self.installer.reinstallProducts(['repodono.storage'])
        self.assertEqual(
            registry['repodono.storage.backend_root'],
            u'/tmp',
        )


class TestUninstall(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['repodono.storage'])

    def test_product_uninstalled(self):
        """Test if repodono.storage is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled('repodono.storage'))

    def test_browserlayer_removed(self):
        """Test that IRepodonoStorageLayer is removed."""
        from repodono.storage.interfaces import IRepodonoStorageLayer
        from plone.browserlayer import utils
        self.assertNotIn(IRepodonoStorageLayer, utils.registered_layers())
