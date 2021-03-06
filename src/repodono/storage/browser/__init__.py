# -*- coding: utf-8 -*-
import json
from collections import namedtuple

from Acquisition import aq_inner
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

from repodono.storage.interfaces import IStorage


# While there are only effectively four fields needed per object (its
# basename (Title), url (getURL), date (ModificationDate), file size
# (getObjSize), there are other attributes are needed for compatibility
# reason with the various javascript libraries used to render the list
# of files (backbone, structure-pattern).  Every required field
# (including overridden fields) are labeled here:
attributes = [
    'Title',  # structure-pattern: for representation of label per row
    'getURL',  # structure-pattern: for the representation of link
    'viewURL',  # structure-pattern-mod: for the view link
    'ModificationDate',  # actual data
    'getObjSize',  # actual data
    'is_folderish',  # structure-pattern: to show that this is a folder
    'portal_type',  # structure-pattern: for the icon
    'id',  # Backbone.Collection.get, unique id for bulk removal.
    'UID',  # structure-pattern: SelectionWellView template
    'path',  # structure-pattern: path
]


# Called brain because originally instances of this were fed into a
# subclass of the default implementation of the BaseVocabularyView.
FileBrain = namedtuple('FileBrain', attributes)


@implementer(IPublishTraverse)
class StorageBrowserView(BrowserView):

    commit = None
    view_name = None

    def __init__(self, *a, **kw):
        super(StorageBrowserView, self).__init__(*a, **kw)
        self.subpath = []
        self.view_name = self.view_name or self.__name__
        self.view_url = '/'.join(
            (self.context.absolute_url(), self.view_name))

    def get_path(self, *filepath):
        return '/'.join(['', self.commit or ''] + list(filepath))

    def get_current_path(self):
        return self.get_path(*self.subpath)

    def get_url(self, filepath):
        return '/'.join([self.view_url, self.commit, filepath])

    def publishTraverse(self, request, name):
        if self.commit is None:
            self.commit = name
        else:
            self.subpath.append(name)
        return self

    def update(self):
        raise NotImplementedError  # pragma: no cover

    def render(self):
        return super(StorageBrowserView, self).__call__()

    def __call__(self):
        self.update()
        return self.render()


class StorageVocabularyView(StorageBrowserView):

    # this references the **parent** view_name as the URLs ultimately
    # gets consumed/presented by that.
    view_name = 'storage_contents'
    commit = None
    subpath = None  # needs overriding to []

    def get_items(self):
        storage = IStorage(self.context)
        storage.datefmt = 'rfc3339.local'
        if self.commit:
            storage.checkout(self.commit)
        # use the normalized revision identifier.
        self.commit = storage.rev

        def pathinfo(p):
            return p, storage.pathinfo(p)

        fileinfo = sorted(
            (
                pathinfo('/'.join(self.subpath + [fn]))
                for fn in storage.listdir('/'.join(self.subpath))
            ),
            key=lambda x: (x[1]['type'] == 'file', x[1]['basename']))

        results = []

        for filepath, info in fileinfo:
            # for the styling.
            if info['type'] == 'file':
                info['type'] = 'document'

            url = self.get_url(filepath)
            fb = FileBrain(
                info['basename'],
                url,
                url,
                info['date'],
                info['size'],
                info['type'] == 'folder',
                info['type'],
                filepath,  # a simple unique id.
                filepath,  # a simple unique id.
                '/' + storage.rev + '/' + filepath,
            )
            results.append(fb._asdict())

        return results

    def __call__(self):
        self.request.response.setHeader('Content-type', 'application/json')

        try:
            items = self.get_items()
        except KeyError:  # trap all related errors
            raise NotFound(self.context, self.context.title_or_id())

        total = len(items)
        return json.dumps({
            'results': items,
            'total': total,
        })


@implementer(IFolderContentsView)
class StorageContentsView(StorageBrowserView):

    def get_actions(self):
        # actions = []
        # XXX returning a dummy with one item that does nothing because
        # there is no way to disable the action bar (can't override the
        # `demoButtons` that gets injected if `buttons` is empty.

        # Real implementation, if it is desired (say for generating
        # static pages from a file) will be done similar to how the
        # folder_contents view actually produce this.
        return []

    def update(self):
        base_url = self.context.absolute_url()
        base_vocabulary = '%s/@@getStorageVocabulary' % base_url
        push_state_url = '%s/storage_contents{path}' % base_url
        options = {
            'vocabularyUrl': base_vocabulary,
            'pushStateUrl': push_state_url,
            'traverseView': True,
            # TODO verify that get_url result in a valid location dir.
            'traverseSubpath': self.get_current_path(),
            'indexOptionsUrl': '%s/@@qsOptions' % base_url,
            'contextInfoUrl': '%s/@@sc-contextInfo' % base_url,
            'attributes': attributes,
            'activeColumns': ['ModificationDate', 'getObjSize'],
            'activeColumnsCookie': 'activeStorageColumns',
            'availableColumns': {
                'id': translate(_('ID'), context=self.request),
                'ModificationDate': translate(_('Last modified'), context=self.request),  # noqa
                'getObjSize': translate(_('Object Size'), context=self.request),  # noqa
            },
            'upload': False,
            'rearrange': False,
            'buttons': self.get_actions(),
            'menuGenerator': 'repodonostorage-url/js/actionmenu',
            'tableRowItemAction': {
                # switch off the default navigation js method
                'other': None,
            },
            'collectionConstructor': 'repodonostorage-url/js/collection',
        }
        self.options = json.dumps(options)


class StorageContextInfo(BrowserView):
    """
    This provides the context information for the object that implements
    IStorage.
    """

    attributes = ['Title', 'Type', 'path',
                  'is_folderish', 'Subject', 'getURL', 'id',
                  'getObjSize', 'portal_type']

    def __call__(self):
        context = aq_inner(self.context)
        storage = IStorage(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            brains = catalog(UID=IUUID(self.context))
        except TypeError:  # pragma: no cover
            brains = []
        item = None
        if len(brains) > 0:
            obj = brains[0]
            base_path = '/'.join(context.getPhysicalPath())
            item = {}
            for attr in self.attributes:
                key = attr
                if key == 'path':
                    attr = 'getPath'
                val = getattr(obj, attr, None)
                if callable(val):
                    val = val()
                if key == 'path':
                    val = val[len(base_path):]
                item[key] = val
        return json.dumps({
            'addButtons': [],
            'defaultPage': self.context.getDefaultPage(),
            'object': item,
            'branches': storage.branches(),
            'tags': storage.tags(),
            'defaultRev': storage.rev,  # no checkout should have been done
        })
