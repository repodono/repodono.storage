# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

from .annotation import annotator
from .interfaces import IStorage
from .interfaces import IStorageBackend
from .interfaces import IStorageFactory
from .interfaces import IStorageInfo


# TODO implement a null implementation for placeholder - a dummy that
# provides no actual data that is returned when the real item cannot
# be adapted, in the case where the package that supplied that
# implementation was removed.

@implementer(IStorage)
class BaseStorage(object):

    _default_datefmt = {
        'rfc2822': '%a, %d %b %Y %H:%M:%S +0000',
        'rfc3339': '%Y-%m-%dT%H:%M:%SZ',
        'iso8601': '%Y-%m-%d %H:%M:%S',
    }

    _datefmt = 'iso8601'

    @property
    def datefmt(self):
        _default = 'iso8601'
        return ((self._datefmt in self._default_datefmt)
                and self._datefmt or _default)

    @datefmt.setter
    def datefmt(self, value):
        if value in self._default_datefmt:
            self._datefmt = value
        else:
            raise ValueError('unsupported datetime format')

    @property
    def datefmtstr(self):
        return self._default_datefmt.get(self.datefmt, '%Y-%m-%d %H:%M:%S')

    def __init__(self, context):
        self.context = context

    def basename(self, path):
        raise NotImplementedError

    def checkout(self, rev=None):
        raise NotImplementedError

    def file(self, path):
        raise NotImplementedError

    def files(self):
        raise NotImplementedError

    def listdir(self, path):
        raise NotImplementedError

    def log(self, start, count, branch=None):
        raise NotImplementedError

    def pathinfo(self, path):
        raise NotImplementedError


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
