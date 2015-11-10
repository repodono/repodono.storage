# -*- coding: utf-8 -*-
from zope.component import queryUtility
from zope.component import getSiteManager
from zope.schema.interfaces import IVocabularyFactory

from repodono.storage.interfaces import IStorageBackend
from repodono.storage.vocab import StorageBackendAvailableVocabFactory
from repodono.storage.vocab import StorageBackendEnabledVocabFactory

from repodono.storage.testing import REPODONO_STORAGE_INTEGRATION_TESTING
from repodono.storage.testing.storage import DummyStorageBackend

import unittest


class StorageVocabTestCase(unittest.TestCase):

    layer = REPODONO_STORAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_base(self):
        vocab = StorageBackendAvailableVocabFactory()(None)
        self.assertEqual(list(vocab), [])
        vocab = StorageBackendEnabledVocabFactory()(None)
        self.assertEqual(list(vocab), [])

        vocab = queryUtility(
            IVocabularyFactory, name='repodono.storage.backends')(None)
        self.assertEqual(list(vocab), [])

        vocab = queryUtility(
            IVocabularyFactory,
            name='repodono.storage.available_backends')(None)
        self.assertEqual(list(vocab), [])

    def test_term(self):
        getSiteManager().registerUtility(
            DummyStorageBackend(), IStorageBackend, name='dummy_storage')

        vocab = StorageBackendAvailableVocabFactory()(None)
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').token, 'dummy_storage')
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').value, 'dummy_storage')

        vocab = queryUtility(
            IVocabularyFactory,
            name='repodono.storage.available_backends')(None)
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').token, 'dummy_storage')
        self.assertEqual(vocab.getTermByToken(
            'dummy_storage').value, 'dummy_storage')
