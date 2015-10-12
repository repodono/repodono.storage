# -*- coding: utf-8 -*-
from zope.interface import implementer

from .annotation import annotator
from .interfaces import IStorage
from .interfaces import IStorageBackend
from .interfaces import IStorageInfo


@implementer(IStorage)
class BaseStorage(object):

    def __init__(self, context):
        self.context = context


@implementer(IStorageBackend)
class BaseStorageBackend(object):
    """
    The base storage backend utility
    """


@annotator(IStorageInfo)
class StorageInfo(object):
    pass
