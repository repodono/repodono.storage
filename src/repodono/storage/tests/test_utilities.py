# -*- coding: utf-8 -*-
from zope.component import queryUtility
from zope.component import getSiteManager
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import WrongContainedType

from plone.registry.interfaces import IRegistry

from repodono.storage.interfaces import IStorageBackend
from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing.storage import DummyStorageBackend
from repodono.storage import utilities

import unittest


class AblerBackendTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_base(self):
        vocab = queryUtility(
            IVocabularyFactory, name='repodono.storage.backends')(None)
        self.assertEqual(list(vocab), [])

    def test_registered_enable_disable(self):
        getSiteManager().registerUtility(
            DummyStorageBackend(), IStorageBackend, name='dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory, name='repodono.storage.backends')(None)
        self.assertEqual(list(vocab), [])

        utilities.enable_backend('dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory, name='repodono.storage.backends')(None)
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').token, 'dummy_storage')

        utilities.enable_backend('dummy_storage')

    def test_unregistered_enable_disable(self):
        with self.assertRaises(WrongContainedType):
            utilities.enable_backend('dummy_storage')

    def test_enabled_uninstalled(self):
        dsb = DummyStorageBackend()
        getSiteManager().registerUtility(
            dsb, IStorageBackend, name='dummy_storage')
        utilities.enable_backend('dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory, name='repodono.storage.backends')(None)
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').token, 'dummy_storage')

        getSiteManager().unregisterUtility(
            dsb, IStorageBackend, name='dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory, name='repodono.storage.backends')(None)
        self.assertEqual(list(vocab), [])

        # registry should be untouched at this point
        registry = queryUtility(IRegistry)
        self.assertEqual(
            registry['repodono.storage.enabled_backends'], [u'dummy_storage'])

        # shouldn't break anything.
        utilities.disable_backend('unrelated')
        self.assertEqual(list(vocab), [])

        # The bad value is no longer stored.
        self.assertEqual(
            registry['repodono.storage.enabled_backends'], [])
