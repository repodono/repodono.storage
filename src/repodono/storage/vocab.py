# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import getUtilitiesFor
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from repodono.storage.interfaces import IStorageBackend


@implementer(IVocabularyFactory)
class StorageBackendAvailableVocabFactory(object):

    def __call__(self, context):
        self.context = context
        terms = []

        for name, utility in getUtilitiesFor(IStorageBackend):
            # TODO define standard i18n the title for implementations
            title = name
            terms.append(SimpleVocabulary.createTerm(name, name, title))

        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class StorageBackendEnabledVocabFactory(object):

    def __call__(self, context):
        self.context = context
        terms = []

        registry = getUtility(IRegistry)
        for name, utility in getUtilitiesFor(IStorageBackend):
            if name not in registry['repodono.storage.enabled_backends']:
                continue
            # TODO define standard i18n the title for implementations
            title = name
            terms.append(SimpleVocabulary.createTerm(name, name, title))

        return SimpleVocabulary(terms)
