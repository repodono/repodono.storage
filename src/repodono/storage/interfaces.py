# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope import schema

from repodono.storage import _


class IRepodonoStorageLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IStorageInfo(Interface):
    """
    Storage information

    The fields defined here are the minimum required information to
    instantiate a Storage instance for a given context that implements
    IWorkspace.

    The actual implementation should be a generic class to ensure
    portability.
    """

    path = schema.TextLine(
        title=_(u'Path'),
        description=_(u'The absolute path on the file system for this object'),
        required=False,
    )

    backend = schema.Choice(
        title=_(u'Backend'),
        required=True,
        vocabulary='repodono.storage.backend',
    )


class IStorage(Interface):
    """
    Common storage class used by the workspace implementation.
    """


class IStorageBackend(Interface):
    """
    The utility that instantiates and manages the storage instances.
    There is an implementation per storage type.
    """
