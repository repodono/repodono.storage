from zope.interface import implementer

from .annotation import factory
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

@factory(IStorageInfo)
class StorageInfo(object):
    pass
