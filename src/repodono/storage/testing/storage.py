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


class DummyStorageBackend(BaseStorageBackend):
    """
    Dummy backend based on data in a dictionary in memory.
    """

    def __init__(self):
        self._data = {}

    def acquire(self, context):
        return DummyStorage(context)

    def install(self, context):
        pass

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
    pass


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
