from zope.interface import implementer

from .interfaces import IStorage
from .interfaces import IStorageBackend


@implementer(IStorage)
class BaseStorage(object):

    def __init__(self, context):
        self.context = context


@implementer(IStorageBackend)
class BaseStorageBackend(object):
    """
    The base storage backend utility
    """


# standard annotation
class StorageInfo(object):

    def __init__(self, context):
        pass
        # need to provide function to get id/path to object, and generate
        # one based on standard globbing rules.  This will be fixed and
        # not changed.
        # self.path = generate_path(context)
        # Also need to figure out how to define access - either via
        # interface tagging or something else.
