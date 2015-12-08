# -*- coding: utf-8 -*-
from os.path import join
from os.path import exists
from os.path import split
from os import listdir
from os import makedirs
import re

from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from plone.registry.interfaces import IRegistry

from .annotation import annotator
from .interfaces import IStorage
from .interfaces import IStorageBackend
from .interfaces import IStorageBackendFSAdapter
from .interfaces import IStorageFactory
from .interfaces import IStorageInfo
from .interfaces import IStorageRegistry


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
        storage_backend_fs = queryMultiAdapter(
            (backend, self.context), IStorageBackendFSAdapter)
        if storage_backend_fs is not None:
            storage_backend_fs.install()
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


@implementer(IStorageBackendFSAdapter)
class DefaultStorageBackendFSAdapter(object):

    makedir_retry = 10

    def __init__(self, backend, context):
        """
        Constructor
        """

        self.backend = backend
        self.context = context

    def get_root(self):
        """
        Get the root directory associated with the manager.
        """

        registry = getUtility(IRegistry)
        p = registry.forInterface(IStorageRegistry, prefix='repodono.storage')
        return p.backend_root

    def _get_path(self):
        """
        Helper method to resolve default path for the given context.
        """

        return join(self.get_root(), *self.context.getPhysicalPath())

    def find_next_path(self, path):
        dirn, basen = split(path)
        dirs = listdir(dirn)
        return join(dirn, self._find_next_path(dirs, basen))

    def _find_next_path(self, names, basen):
        def split(p):
            x, i = p.rsplit('-', 1)
            return x, int(i)

        def unsplit_next(x, i):
            return x + '-' + str(i + 1)

        pattern = re.compile('^%s-[0-9]+$' % basen)
        paths = sorted((split(n) for n in names if pattern.match(n)),
                       key=lambda x: x[1])
        if paths:
            return unsplit_next(*paths[-1])
        # start the number.
        return basen + '-1'

    def _makedirs(self, path):
        count = self.makedir_retry
        target_path = path

        while count >= 0:
            try:
                makedirs(target_path)
            except OSError:
                target_path = self.find_next_path(path)
            else:
                return target_path
            count -= 1

        raise ValueError('Failed to make a dir')

    def install(self):
        """
        Create a directory for the given context, and associate it to
        the IStorageInfo annotation.

        Subclasses can introduce more specific annotator.
        """

        info = IStorageInfo(self.context)

        default = self._get_path()
        info.path = self._makedirs(default)

    def acquire(self):
        """
        Acquire the name of the directory associated for the given
        context.
        """

        subpath = IStorageInfo(self.context).path

        if subpath is None:
            raise ValueError('context has no IStorageInfo.path annotated.')

        target = join(self.get_root(), subpath)

        if not exists(target):
            raise ValueError(
                'Directory associated with context does not exists.')

        return target


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

    storage_factory = IStorageFactory(context)
    storage_factory.backend = backend
    storage_factory.install_storage()


def storage_adapter(context):
    return IStorageFactory(context)()
