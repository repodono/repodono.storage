from zope.interface import implementer
from zope.component import adapter
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from repodono.storage.interfaces import IStorageInfo

PREFIX = __name__  # this module name


def to_key(prefix, name):
    return prefix + '.' + name

def _setup_dict_annotation(context, key):
    annotations = IAnnotations(context)
    if not key in annotations:
        annotations[key] = PersistentDict()
        return True

def _teardown_dict_annotation(context, key):
    annotations = IAnnotations(context)
    if key in annotations:
        del annotations[key]
        return True

def factory(iface, _key=None):
    """
    Factory that takes a class and an interface to construct a new class
    that provides helper classmethods to the above functions (as a pair
    of install/uninstall methods) and also an adapter to an IAnnotatable
    that returns an object with the fields specified in the interface
    iface, while also implementing that interface.

    The resulting object acts as a view to the attributes.  This means
    an explicit write action is required to persist the value back into
    the annotation.
    """

    # need the key argument but not the iface is due to python being
    # python

    def decorator(class_):
        # Can't reassign the argument defined in the decorator factory
        # function due to how binding in closures apparently (don't)
        # work in Python, hence that argument is _key and is assigned to
        # a different identifier which will be used from here and inside
        # the class.
        key = _key

        if key is None:
            key = to_key(class_.__module__, class_.__name__)

        @adapter(IAnnotatable)
        @implementer(iface)
        class Annotation(class_):
            def __init__(self, context, *a, **kw):
                annotations = IAnnotations(context)
                if not key in annotations:
                    raise TypeError('Could not instantiate a `%s` from %s' %
                        (key, context))
                d = annotations[key]
                for name in iface.names():
                    setattr(self, name, d.get(name))
                # finally associate context to the instance.
                self.context = context

                super(class_, self).__init__(*a, **kw)

            @classmethod
            def install(cls, context):
                """
                Setup a persistent dictionary as an annotation to the
                context.
                """

                _setup_dict_annotation(context, key)

            @classmethod
            def uninstall(cls, context):
                """
                Completely removes the annotation from context.
                """

                _teardown_dict_annotation(context, key)

        return type(class_.__name__, (Annotation, class_), {})

    return decorator
