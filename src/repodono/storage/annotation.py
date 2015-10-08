from zope.interface import implementer
from zope.component import adapter
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from repodono.storage.interfaces import IStorageInfo

PREFIX = __name__  # this module name


def to_key(prefix, name):
    return prefix + '.' + name

def _setup_dict_annotation(context, name, prefix=PREFIX):
    annotations = IAnnotations(context)
    key = to_key(prefix, name)
    if not key in annotations:
        annotations[key] = PersistentDict()
        return True

def _teardown_dict_annotation(context, name, prefix=PREFIX):
    annotations = IAnnotations(context)
    key = to_key(prefix, name)
    if key in annotations:
        del annotations[key]
        return True


@adapter(IAnnotatable)
@implementer(IStorageInfo)
class StorageInfo(object):
    """
    This StorageInfo implementation effectively presents a view for the
    underlying persistent data, making direct manipulation of the fields
    not readily possible.  Should not be a problem as those fields
    should be effectively "frozen" after its creation due to the nature
    of the static definition of most storage backends in the point of
    view of end users.
    """

    def __init__(self, context):
        """
        Adapts context into a StorageInfo, assumes install was already
        called on the context.
        """

        annotations = IAnnotations(context)
        cls = self.__class__
        key = to_key(cls.__module__, cls.__name__)
        if not key in annotations:
            raise TypeError('Could not instantiate a `%s` from %s' %
                (key, context))
        d = annotations[key]
        # default should be IStorageInfo.  Subclasses implementing an
        # interface that extends off IStorageInfo may have other fields.
        iface = self.__implemented__.interfaces().next()
        for name in iface.names():
            setattr(self, name, d.get(name))
        # finally associate context to the instance.
        self.context = context

    @classmethod
    def install(cls, context):
        """
        Setup a persistent dictionary as an annotation to the context.
        This annotation can be instantiated as a StorageInfo.
        """

        _setup_dict_annotation(context, cls.__name__, cls.__module__)

    @classmethod
    def uninstall(cls, context):
        """
        Completely removes the StorageInfo annotation.
        """

        _teardown_dict_annotation(context, cls.__name__, cls.__module__)
