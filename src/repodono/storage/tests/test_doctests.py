# -*- coding: utf-8 -*-
from plone.testing import layered
import doctest
import unittest
from repodono.storage.testing import REPODONO_DUMMY_STORAGE_FUNCTIONAL_TESTING


tests = (
    'storage.txt',
)


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
                 layer=REPODONO_DUMMY_STORAGE_FUNCTIONAL_TESTING)
            for f in tests]
    )
