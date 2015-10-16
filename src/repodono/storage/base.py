# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

from .annotation import annotator
from .interfaces import IStorage
from .interfaces import IStorageBackend
from .interfaces import IStorageFactory
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

    def acquire(self, context):
        raise NotImplementedError

    def install(self, context):
        raise NotImplementedError


@annotator(IStorageFactory)
class StorageFactory(object):
    """
    The default storage factory annotation.
    """

    backend = FieldProperty(IStorageFactory['backend'])

    def install_storage(self):
        backend = self.get_storage_backend()
        backend.install(self.context)

    def get_storage(self):
        backend = self.get_storage_backend()
        return backend.acquire(self.context)

    def get_storage_backend(self):
        return getUtility(IStorageBackend, name=self.backend)

    def __call__(self):
        return self.get_storage()


@annotator(IStorageInfo)
class StorageInfo(object):
    pass


def storage_installer(context, backend):
    """
    Install a storage identified by name into context.

    context
        The context to have a storage installed.
    backend
        The name of the storage backend.
    """

    # Initialize a storage factory for the context and assign a backend,
    # which must be valid (checking done via vocabulary schema).
    # TODO explore usage of marker interface instead.
    storage_factory = IStorageFactory(context)
    storage_factory.backend = backend
    storage_factory.install_storage()


def storage_adapter(context):
    return IStorageFactory(context)()
