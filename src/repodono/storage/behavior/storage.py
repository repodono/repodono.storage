# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import provider
from zope.interface import alsoProvides

from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives
from plone.supermodel import model
from z3c.form.interfaces import IAddForm

from repodono.storage import _
from repodono.storage.interfaces import IStorageEnabled
from repodono.storage.interfaces import IStorageFactory
from repodono.storage.base import StorageFactory


@provider(IFormFieldProvider)
class IStorageEnabler(model.Schema):
    """
    Originally defined to be the surrogate interface for the addition of
    a new StorageFactory to a context and to avoid the problems of using
    the same interface that defines the enabling of the storage behavior
    (IStorageEnabled), this is now formalized to include the definitions
    required to enable a proper integration with dexterity.
    """

    model.fieldset('storage', label=u"Storage",
                   fields=['backend'])

    backend = schema.Choice(
        title=_(u'Backend'),
        description=_(u'The identifier for the backend.'),
        required=True,
        vocabulary='repodono.storage.backends',
    )

    directives.omitted('backend')
    directives.no_omit(IAddForm, 'backend')


def StorageEnabler(context):
    """
    The companion factory for the above behavior interface.
    """

    if not IStorageEnabled.providedBy(context):
        alsoProvides(context, IStorageEnabled)
    return StorageFactory(context)


def StorageCreate(obj, event):
    """
    The companion factory for the above behavior interface.
    """

    factory = IStorageFactory(obj)
    factory.install_storage()
