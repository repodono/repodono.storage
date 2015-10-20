# -*- coding: utf-8 -*-
from glob import glob
from os.path import join
from os.path import relpath
from os import walk

from repodono.storage.base import BaseStorageBackend
from repodono.storage.base import BaseStorage
from repodono.storage.interfaces import IStorageInfo


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
            raise ValueError(
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

    @property
    def rev(self):
        return self._rev

    def checkout(self, rev=None):
        if rev is None:
            rev = str(len(self._data()) - 1)

        self._rev = rev


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
