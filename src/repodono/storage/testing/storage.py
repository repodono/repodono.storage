# -*- coding: utf-8 -*-
from repodono.storage.base import BaseStorageBackend
from repodono.storage.base import BaseStorage
from repodono.storage.interfaces import IStorageInfo


class IDummyStorageInfo(IStorageInfo):
    """
    Information for the dummy storage info.
    """

    # maybe add an extra attribute for testing purposes.


class DummyStorageBackend(BaseStorageBackend):
    pass


class DummyStorage(BaseStorage):
    pass
