from zope.schema.interfaces import WrongType
from zope.interface.interface import Method
from zope.interface import implementer
from zope.component import adapter
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from persistent.mapping import PersistentMapping

from repodono.storage.interfaces import IStorageInfo

_marker = object()


def to_key(prefix, name):
    return prefix + '.' + name

def _setup_dict_annotation(context, key):
    annotations = IAnnotations(context)
    if not key in annotations:
        annotations[key] = PersistentMapping()
        return annotations[key]

def _teardown_dict_annotation(context, key):
    annotations = IAnnotations(context)
    if key in annotations:
        result = dict(annotations[key])
        del annotations[key]
        return result

def _iface_fields(iface):
    return [n for n, v in iface.namesAndDescriptions(all=True)
            if not isinstance(v, Method)]

def factory(iface, _key=None):
    """
    A class decorator to a class to turn it into an annotation that
    requires an explicit installation and backed by a PersistentMapping,
    instead of the usual implicit method that has the potential to leave
    behind stale objects to classes that may no longer exist.

    This works like a factory that will take a class and an interface,
    returning a new class that implements the interface.  This new class
    is able to adapt any IAnnotatable, provided that the context was
    previously installed with the classmethod ``install``.

    An ``uninstall`` classmethod is also provided which will remove the
    PersistentMapping identified by key.

    Naturally, the class can contain ``FieldProperty`` properties that
    are based on the interface schema that is about to be implemented by
    this.
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

        classname = to_key(class_.__module__, class_.__name__)
        if key is None:
            key = classname

        names = _iface_fields(iface)

        @adapter(IAnnotatable)
        @implementer(iface)
        class Annotation(class_):
            def __init__(self, context, *a, **kw):
                annotations = IAnnotations(context)
                if not key in annotations:
                    raise TypeError('Could not instantiate a `%s` from %s '
                        'with Annotation `%s`' % (classname, context, key))
                d = annotations[key]
                for name in names:
                    value = d.get(name, _marker)
                    if value is _marker:
                        # undefined values are not touched, only define
                        # the attribute on the instance if it doesn't
                        # already exist
                        if hasattr(self, name):
                            continue

                    # set the loaded value to the instance only.
                    try:
                        super(Annotation, self).__setattr__(name, d.get(name))
                    except WrongType as e:
                        raise TypeError('Could not assign attribute `%s` to '
                            'class `%s` with value from Annotation `%s` due '
                            'to `%s`.' % (name, classname, key, e.__repr__()))

                # finally associate context to the instance.
                super(Annotation, self).__setattr__('context', context)

                super(class_, self).__init__(*a, **kw)

            def __setattr__(self, name, value):
                """
                Whenever an attribute is set, persist it into the
                underyling PersistentMapping.
                """

                super(Annotation, self).__setattr__(name, value)
                if name not in names:
                    return
                annotations = IAnnotations(self.context)
                d = annotations[key]
                d[name] = value

            @classmethod
            def install(cls, context):
                """
                Setup a persistent dictionary as an annotation to the
                context.
                """

                return _setup_dict_annotation(context, key)

            @classmethod
            def uninstall(cls, context):
                """
                Completely removes the annotation from context.
                """

                return _teardown_dict_annotation(context, key)

        return type(class_.__name__, (Annotation,), {})

    return decorator
