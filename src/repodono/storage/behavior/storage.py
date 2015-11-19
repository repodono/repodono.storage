# -*- coding: utf-8 -*-
from types import MethodType
from logging import getLogger
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import provider
from zope.component import ComponentLookupError
from zope.component import getUtility

from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives
from plone.supermodel import model
from z3c.form.interfaces import IAddForm
from z3c.form.browser.select import SelectFieldWidget
from z3c.form.interfaces import DISPLAY_MODE

from repodono.storage import _
from repodono.storage.interfaces import IStorageFactory

logger = getLogger(__name__)


# If this is generalized, this might be doable
# @zope.component.adapter(zope.schema.interfaces.IDisplayIfEmptyChoice,
#                         zope.interface.Interface,
#                         z3c.form.interfaces.IFormLayer)
# @zope.interface.implementer(IFieldWidget)
def DisplayIfEmptySelectFieldWidget(field, source, request=None):
    """Checks vocabulary, if empty, force display mode"""
    widget = SelectFieldWidget(field, source, request)
    if field.vocabulary:
        # has vocabulary
        return widget
    # Alternatively, adapt for the z3c version of terms?
    # zope.component.getMultiAdapter(
    #     (None, request, None, field, SelectWidget(request)),
    #     interfaces.ITerms)
    vocab = getUtility(
        schema.interfaces.IVocabularyFactory, name=field.vocabularyName)(None)
    if not len(vocab):
        # bind a new update to disable display mode
        old_update = widget.update

        def update(self):
            old_update()
            self.mode = DISPLAY_MODE
            # Provide an alternative vocabulary that supply the text
            # for the lack of choice.
            value = [_(u'<no choices are available>')]
            self.terms = SimpleVocabulary.fromValues(value)
            self.value = value
        widget.update = MethodType(update, widget)
    return widget


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
    directives.widget(backend=DisplayIfEmptySelectFieldWidget)


def install_storage(obj, event):
    """
    The event handler for installing and associating a storage to an
    ``IStorageEnabled`` object.
    """

    factory = IStorageFactory(obj)
    try:
        factory.get_storage_backend()
    except ComponentLookupError as e:
        iface, name = e.args
        logger.warning(
            'Could not find storage backend "%s" while creating a "%s", '
            'skipping backend instantiation.', name, obj.portal_type)
    else:
        # the specific backend instance may do further component lookups
        # and fail, which this doesn't and shouldn't care about.
        factory.install_storage()
