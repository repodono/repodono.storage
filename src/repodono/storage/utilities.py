# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.component import getUtilitiesFor
from plone.registry.interfaces import IRegistry
from repodono.storage.interfaces import IStorageBackend


def enable_backend(name):
    """
    Enable the use the backend that is identified by ``name``.
    """

    registry = getUtility(IRegistry)
    original = registry['repodono.storage.enabled_backends']
    registry['repodono.storage.enabled_backends'] = original + [name]


def disable_backend(name):
    """
    Enable the use the backend that is identified by ``name``.
    """

    enabled = sorted(
        n for n, utility in getUtilitiesFor(IStorageBackend)
        if n != name
    )

    registry = getUtility(IRegistry)
    registry['repodono.storage.enabled_backends'] = enabled
