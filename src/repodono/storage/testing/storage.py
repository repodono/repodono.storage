# -*- coding: utf-8 -*-
from datetime import datetime
from logging import getLogger
from glob import glob
from os.path import join
from os.path import dirname
from os.path import relpath
from os import walk
import json

from zope.component import getMultiAdapter

from repodono.storage.base import BaseStorageBackend
from repodono.storage.base import BaseStorage
from repodono.storage.interfaces import IStorageInfo
from repodono.storage.interfaces import IStorageBackendFSAdapter

from repodono.storage.exceptions import PathNotDirError
from repodono.storage.exceptions import PathNotFoundError
from repodono.storage.exceptions import RevisionNotFoundError
from repodono.storage.exceptions import StorageNotFoundError

logger = getLogger(__name__)
path = lambda p: join(dirname(__file__), 'data', p)


def readfile(fullpath):
    with open(fullpath) as fd:
        return fd.read()


def get_dummy_id(context):
    # TODO figure out a better testing strategy once this is figured otu.
    # TODO figure out whether to use the following interface
    try:
        id_ = IStorageInfo(context).path
    except TypeError:  # for a ZCA-less implementation/fallback
        id_ = context.id
    return id_


class IDummyStorageInfo(IStorageInfo):
    """
    Information for the dummy storage info.
    """

    # maybe add an extra attribute for testing purposes.


class DummyStorageData(object):
    """
    Holds the backend data.
    """

    _data = {}

    @classmethod
    def teardown(cls):
        cls._data.clear()


class DummyStorageBackend(BaseStorageBackend):
    """
    Dummy backend based on data in a dictionary in memory.
    """

    def __init__(self):
        self._data = DummyStorageData._data

    def acquire(self, context):
        if get_dummy_id(context) not in self._data:
            raise StorageNotFoundError(
                "context does not have a storage instance installed")
        result = DummyStorage(context)
        return result

    def install(self, context):
        # TODO id generator for uniqueness, instead of relying on the
        # one provided by context, especially since with pure dexterity
        # it can result in a newly created one that lacks one.
        id_ = unicode(context.id)

        try:
            info = IStorageInfo(context)
            info.path = id_
        except TypeError:
            # ZCA-less, ignore.
            pass
        if id_ not in self._data:
            self._data[id_] = [{}]

    def load_dir(self, id_, root):
        result = [
            {
                relpath(join(r, f), p): readfile(join(r, f))
                for r, _, files in walk(p)
                for f in files
            }
            for p in sorted(glob(join(root, '*')))
        ]
        for changeset in result:
            if changeset.get('.dummystoragerc'):
                f = changeset.get('.dummystoragerc')
                try:
                    j = json.loads(f)
                    if not isinstance(j, dict):  # pragma: no cover
                        raise ValueError
                except ValueError:  # pragma: no cover
                    logger.warning(
                        'The `.dummystoragerc` provided in `%s` is invalid',
                        root,
                    )
                else:
                    externals = {}
                    for path, v in j.iteritems():
                        if (v.get('type') == 'subrepo' and
                                isinstance(v.get('rev'), unicode) and
                                isinstance(v.get('location'), unicode)):
                            externals[path] = v
                    changeset.update(externals)

        self._data[id_] = result


class DummyStorage(BaseStorage):

    _backend = None

    def __init__(self, context):
        super(DummyStorage, self).__init__(context)
        self.checkout()

    def _datetime(self, rev=None):
        i = rev
        if rev is None:
            i = self._rev
        ts = datetime.utcfromtimestamp(i * 9876 + 1111111111 + 46800)
        return self.strftime(ts)

    def _data(self):
        rawdata = DummyStorageData._data
        return rawdata[get_dummy_id(self.context)]

    def _get_changeset(self, rev):
        try:
            return self._data()[rev]
        except IndexError:
            raise RevisionNotFoundError()

    def _validate_rev(self, rev):
        """
        Internal use, validates that a rev is an int and that it is also
        a valid index for context's associated data node.
        """

        if not isinstance(rev, int):
            raise RevisionNotFoundError()

        # ensure this can be fetched.
        self._get_changeset(rev)
        return rev

    @property
    def rev(self):
        return str(self._rev)

    @property
    def shortrev(self):
        # no such thing for dummy but this is required.
        return self.rev

    def basename(self, path):
        return path.rsplit('/')[-1]

    def checkout(self, rev=None):
        if rev is None:
            rev = len(self._data()) - 1
        elif not (isinstance(rev, basestring) and rev.isdigit()):
            raise RevisionNotFoundError()

        self._rev = self._validate_rev(int(rev))

    def files(self):
        return sorted(self._get_changeset(self._rev).keys())

    def file(self, path):
        data = self._get_changeset(self._rev)
        try:
            return data[path]
        except KeyError:
            # try to resolve the subrepo for the top level only.
            frags = path.split('/')
            if len(frags) > 1:
                info = self.file(frags[0])
                if isinstance(info, dict):
                    # return the subrepo information.
                    result = {
                        'path': '/'.join(frags[1:]),
                    }
                    result.update(info)
                    return result
            raise PathNotFoundError()

    def listdir(self, path):
        if path and not path.endswith('/'):
            # root is empty path, and specific paths must end with '/'
            # for the code to work.
            path += '/'
        result = sorted({
            i.replace(path, '').split('/')[0]
            for i in self.files() if i.startswith(path)
        })
        if not result and path:
            raise PathNotDirError()
        return result

    def _logentry(self, rev):
        if rev < 0:
            return
        if rev == 0:
            files = self._get_changeset(0).keys()
            files.sort()
            return '\n'.join(['A:%s' % i for i in files])

        newcs = self._get_changeset(rev)
        oldcs = self._get_changeset(rev - 1)
        results = []
        files = set(oldcs.keys() + newcs.keys())

        for f in files:
            if f not in oldcs:
                results.append('A:%s' % f)
            elif f not in newcs:
                results.append('D:%s' % f)
            elif not oldcs[f] == newcs[f]:
                results.append('C:%s' % f)

        results.sort()
        return '\n'.join(results)

    def log(self, start, count, branch=None, *a, **kw):
        start = self._validate_rev(int(start))
        results = []
        for i in range(start, start - count, -1):
            entry = self._logentry(i)
            if not entry:
                break
            results.append({
                'node': str(i),
                'date': self._datetime(i),
                'author': 'tester <tester@example.com>',
                'desc': entry,
            })
        return results

    def pathinfo(self, path):
        result = {
            'date': self._datetime(self._rev),
            'basename': self.basename(path),
        }

        try:
            contents = self.file(path)
        except PathNotFoundError:
            pass
        else:
            if isinstance(contents, dict):
                return contents
            result['size'] = len(contents)
            result['type'] = 'file'
            return result

        try:
            self.listdir(path)
        except PathNotDirError:
            raise PathNotFoundError()
        else:
            result['size'] = 0
            result['type'] = 'folder'
            return result

    def tags(self):
        # static dummy value for now.
        return (
            ('initial', '0'),
            ('release', '3'),
        )

    def branches(self):
        # static dummy value for now.
        return (
            ('default', '4'),
            ('develop', '1'),
        )


class DummyFSStorageBackend(BaseStorageBackend):
    """
    Dummy backend that provides direct access to file system contents.
    """

    require_fs = True

    def acquire(self, context):
        fshelper = getMultiAdapter((self, context), IStorageBackendFSAdapter)
        return DummyFSStorage(context, fshelper.acquire())

    def install(self, context):
        fshelper = getMultiAdapter((self, context), IStorageBackendFSAdapter)
        fshelper.acquire()


class DummyFSStorage(BaseStorage):

    def __init__(self, context, path):
        super(DummyFSStorage, self).__init__(context)
        self.path = path
