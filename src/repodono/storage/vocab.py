# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import getUtilitiesFor

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from repodono.storage.interfaces import IStorageBackend


@implementer(IVocabularyFactory)
class StorageBackendVocabFactory(object):

    def __call__(self, context):
        self.context = context
        terms = []

        for name, utility in getUtilitiesFor(IStorageBackend):
            # TODO define standard i18n the title for implementations
            title = name
            terms.append(SimpleVocabulary.createTerm(utility, name, title))

        return SimpleVocabulary(terms)
