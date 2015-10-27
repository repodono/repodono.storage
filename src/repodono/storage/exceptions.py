# -*- coding: utf-8 -*-


class StorageNotFoundError(KeyError):
    """
    Storage not found for a given context.
    """


class PathNotFoundError(KeyError):
    """
    Error looking up a path in a storage.
    """


class RevisionNotFoundError(KeyError):
    """
    Error looking up a revision in a storage.
    """


class PathNotDirError(PathNotFoundError):
    """
    Path is not a dir.
    """


class PathNotFileError(PathNotFoundError):
    """
    Path is not a file.
    """
