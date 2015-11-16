# -*- coding: utf-8 -*-
from zope.component import queryUtility
from zope.component import getSiteManager
from zope.schema.interfaces import IVocabularyFactory
# from zope.schema.interfaces import WrongContainedType

from plone.registry.interfaces import IRegistry

from repodono.registry.interfaces import IUtilityRegistry
from repodono.storage.interfaces import IStorageBackend
from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing.storage import DummyStorageBackend

import unittest


class StorageUtilityRegistryBackendTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_base(self):
        vocab = queryUtility(
            IVocabularyFactory,
            name='repodono.storage.backends.available')(None)
        self.assertEqual(list(vocab), [])

        vocab = queryUtility(
            IVocabularyFactory,
            name='repodono.storage.backends')(None)
        self.assertEqual(list(vocab), [])

    def test_vocabulary_registry(self):
        getSiteManager().registerUtility(
            DummyStorageBackend(), IStorageBackend, name='dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory,
            name='repodono.storage.backends.available')(None)
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').token, 'dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory,
            name='repodono.storage.backends')(None)
        self.assertEqual(list(vocab), [])

        registry = queryUtility(IRegistry)
        registry['repodono.storage.backends'] = ['dummy_storage']

        vocab = queryUtility(
            IVocabularyFactory,
            name='repodono.storage.backends')(None)
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').token, 'dummy_storage')

    def test_vocabulary_utilities(self):
        getSiteManager().registerUtility(
            DummyStorageBackend(), IStorageBackend, name='dummy_storage')

        utilities = queryUtility(IUtilityRegistry, 'repodono.storage.backends')
        utilities.enable('dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory, name='repodono.storage.backends')(None)
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').token, 'dummy_storage')

    def test_enabled_uninstalled(self):
        dsb = DummyStorageBackend()
        getSiteManager().registerUtility(
            dsb, IStorageBackend, name='dummy_storage')

        utilities = queryUtility(IUtilityRegistry, 'repodono.storage.backends')
        utilities.enable('dummy_storage')

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
            registry['repodono.storage.backends'], [u'dummy_storage'])

        # shouldn't break anything.
        utilities.disable('unrelated')
        self.assertEqual(list(vocab), [])

        # The bad value is no longer stored.
        self.assertEqual(registry['repodono.storage.backends'], [])
