# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope import schema

from repodono.storage import _


class IRepodonoStorageLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IBaseStorageInfo(Interface):
    """
    The base storage info interface.  Every single storage info must
    inherit from this.
    """

    backend = schema.Choice(
        title=_(u'Backend'),
        description=_(u'The identifier for the backend.'),
        required=True,
        vocabulary='repodono.storage.backend',
    )


class IStorageInfo(IBaseStorageInfo):
    """
    These are the bare minimum, generic attributes required to get a
    backend instantiated.  All of these are associated with a given
    context, can be done via IAnnotation or some other means.
    """

    path = schema.TextLine(
        title=_(u'Path'),
        description=_(u'The path argument that is required to instantiate the '
                      'backend for this context.  The format of the path is '
                      'backend specific.'),
        required=False,
    )


class IStorageFactory(Interface):
    """
    The IStorageFactory is an adapter that will accept a context as part
    of its instantiation, which can then be called again to instantiate
    the IStorage instance, specific to the information in the attributes
    captured by IStorageInfo.

    With ``context`` as a Dexterity item, the verbose instantiation can
    be done like so::

        >>> storage_info = IStorageInfo(context)
        >>> backend = getUtility(IStorageBackend, name=storage_info.backend)
        >>> storage = backend(storage_info)  # for the rest of the arguments.

    The storage factory simply encapsulates the first two lines to
    produce storage instances.  Reason for multiple instances to a given
    context is implementation specific but should be supported here.
    Example::

        >>> storage_factory = IStorageFactory(context)
        >>> storage = storage_factory()

    Ultimately, this should be contracted to::

        >>> storage = IStorage(context)

    The minimum implementation should be a generic class to ensure
    reusability by the users of this framework.
    """

    def get_storage():
        """
        Return the storage instance as defined with the information
        contained with the attributes here.
        """

    def get_storage_backend():
        """
        Return the storage backend defined by backend attribute.
        """


class IStorage(Interface):
    """
    Common storage class used by the workspace implementation.
    """

    def checkout(rev=None):
        """
        Activate the revision identify by the rev.  All file operations
        will now be done against it.

        Default argument of None checks out a default version specific
        to the storage backend, in most cases it will be the latest
        revision.
        """

    def file(path):
        """
        Returns the content at the given path, for the currently
        checked out revision.
        """

    def files():
        """
        Returns the entire listing of all files in the currently
        checked out revision.
        """

    def listdir(path):
        """
        Do a directory listing of `path` in the currently checked out
        revision.
        """

    def log(start, count, branch=None):
        """
        Returns a list of log entries.
        """

    def pathinfo(path):
        """
        Returns the information at the given path, for the currently
        checked out revision.
        """


class IStorageBackend(Interface):
    """
    The utility that instantiates and manages the storage instances.
    There is an implementation per storage type.
    """

    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Human readable title to this storage backend'),
    )

    command = schema.TextLine(
        title=_(u'Command'),
        default=_(u'The name of the binary that is typically associated with '
                  'this storage backend.'),
        required=False,
    )

    clone_verb = schema.TextLine(
        title=_(u'Clone Verb'),
        default=_(u'The command "verb" that the default binary use for making '
                  'a local checkout on user\'s machine.'),
        required=False,
    )

    def adapt_from(context):
        """
        Adapt context into a storage instance.
        """

    def create(context):
        """
        Create or instantiate the backend storage for context.
        """
