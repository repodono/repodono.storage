# -*- coding: utf-8 -*-
import os
from zope.component import adapter
from plone.registry.interfaces import IRecordAddedEvent

from repodono.storage.interfaces import IStorageRegistry


@adapter(IStorageRegistry, IRecordAddedEvent)
def set_default_backend_root(proxy, event):
    if event.record.fieldName == 'backend_root' and event.record.value is None:
        event.record.value = unicode(os.environ.get('CLIENT_HOME'))
