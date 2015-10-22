# -*- coding: utf-8 -*-
from glob import glob
from os.path import join
from os.path import relpath
from os import walk

from repodono.storage.base import BaseStorageBackend
from repodono.storage.base import BaseStorage
from repodono.storage.interfaces import IStorageInfo

from repodono.storage.exceptions import PathNotFoundError
from repodono.storage.exceptions import RevisionNotFoundError
from repodono.storage.exceptions import StorageNotFoundError


def readfile(fullpath):
    with open(fullpath) as fd:
        return fd.read()


class IDummyStorageInfo(IStorageInfo):
    """
    Information for the dummy storage info.
    """

    # maybe add an extra attribute for testing purposes.


class DummyStorageData(object):
    """
    Holds the backend data.
    """

    _data = {}

    @classmethod
    def teardown(cls):
        cls._data.clear()


class DummyStorageBackend(BaseStorageBackend):
    """
    Dummy backend based on data in a dictionary in memory.
    """

    def __init__(self):
        self._data = DummyStorageData._data

    def acquire(self, context):
        if context.id not in self._data:
            raise StorageNotFoundError(
                "context does not have a storage instance installed")
        result = DummyStorage(context)
        return result

    def install(self, context):
        if context.id not in self._data:
            self._data[context.id] = [{}]

    def load_dir(self, id_, root):
        result = [
            {
                relpath(join(r, f), p): readfile(join(r, f))
                for r, _, files in walk(p)
                for f in files
            }
            for p in sorted(glob(join(root, '*')))
        ]
        self._data[id_] = result


class DummyStorage(BaseStorage):

    _backend = None

    def __init__(self, context):
        super(DummyStorage, self).__init__(context)
        self.checkout()

    def _data(self):
        rawdata = DummyStorageData._data
        return rawdata[self.context.id]

    def _get_changeset(self, rev):
        try:
            return self._data()[rev]
        except IndexError:
            raise RevisionNotFoundError()

    def _validate_rev(self, rev):
        """
        Internal use, validates that a rev is an int and that it is also
        a valid index for context's associated data node.
        """

        if not isinstance(rev, int):
            raise RevisionNotFoundError()

        # ensure this can be fetched.
        self._get_changeset(rev)
        return rev

    @property
    def rev(self):
        return str(self._rev)

    def basename(self, path):
        return path.rsplit('/')[-1]

    def checkout(self, rev=None):
        if rev is None:
            rev = len(self._data()) - 1
        elif not (isinstance(rev, basestring) and rev.isdigit()):
            raise RevisionNotFoundError()

        self._rev = self._validate_rev(int(rev))

    def files(self):
        return sorted(self._get_changeset(self._rev).keys())

    def file(self, path):
        data = self._get_changeset(self._rev)
        try:
            return data[path]
        except KeyError:
            raise PathNotFoundError()


class DummyFSStorageBackend(BaseStorageBackend):
    """
    Dummy backend that provides direct access to file system contents.
    """

    def acquire(self, context):
        return DummyFSStorage(context)

    def install(self, context):
        pass


class DummyFSStorage(BaseStorage):
    pass
