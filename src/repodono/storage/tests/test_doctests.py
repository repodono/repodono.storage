# -*- coding: utf-8 -*-
from plone.testing import layered
import doctest
import unittest
from repodono.storage.testing import REPODONO_DUMMY_STORAGE_FUNCTIONAL_TESTING
from repodono.storage.testing import REPODONO_STORAGE_FUNCTIONAL_TESTING


# Ones only need the base implementation.
tests = (
    'storage.txt',
)

# Ones need dummy storage
dummy_tests = (
    'dummy_storage.txt',
)


def test_suite():
    d = [layered(doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
         layer=REPODONO_DUMMY_STORAGE_FUNCTIONAL_TESTING)
         for f in dummy_tests]
    s = [layered(doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
         layer=REPODONO_STORAGE_FUNCTIONAL_TESTING)
         for f in tests]
    return unittest.TestSuite(d + s)
