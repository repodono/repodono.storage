# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope import schema

from repodono.storage import _


class IRepodonoStorageLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IStorageEnabled(Interface):
    """
    Marker interface for objects to enable the usage of Storage.

    The various components are declared to adapt against this interface.
    """


class IStorageInfo(Interface):
    """
    A common minimum set of information required to acquire a storage
    instance
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

    By default this is implemented as an annotation.

    With ``context`` as some IAnnotatable, the verbose instantiation is
    done like so::

        >>> storage_factory = IStorageFactory(context)
        >>> backend = getUtility(IStorageBackend, name=storage_factory.backend)
        >>> storage = backend.acquire(context)

    For simplicity, the method ``get_storage`` simply encapsulates the
    above, and this should simply be callable::

        >>> storage_factory = IStorageFactory(context)
        >>> storage = storage_factory()

    Ultimately, this can be contracted to::

        >>> storage = IStorage(context)

    The minimum implementation should be a generic class to ensure
    reusability by the users of this framework.
    """

    backend = schema.Choice(
        title=_(u'Backend'),
        description=_(u'The identifier for the backend.'),
        required=True,
        readonly=True,
        vocabulary='repodono.storage.backends',
    )

    def install_storage():
        """
        Install a new storage instance and associate it with context.
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

    # Should be a read-only property.
    rev = schema.TextLine(
        title=_(u'Current Revision'),
        description=_(u'The currently active revision'),
        required=True,
    )

    def basename(path):
        """
        Return the basename of the given path.
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

    def acquire(context):
        """
        Acquire a storage instance of this backend from context.
        """

    def install(context):
        """
        Create or instantiate the storage this backend provides for
        context.
        """


class IStorageInstaller(Interface):
    """
    Marker interface for storage installer utility.
    """


class IStorageRegistry(Interface):
    """
    Interface for the fields to be registered into the Plone Registry
    """

    # TODO figure out the datatype, and figure out whether it is a good
    # idea to create another vocabulary just for this if Choice is used.

    active_backends = schema.Text(
        title=_(u'Active Storage Backends'),
        required=False,
    )

    backend_root = schema.TextLine(
        title=_(u'Backend root.'),
        description=_(
            u'The root directory that is used for the filesystem root tool.'
        ),
        required=False,
    )
