# -*- coding: utf-8 -*-
from types import MethodType

from zope.schema.interfaces import WrongType
from zope.interface.interface import Method
from zope.interface import classImplements
from zope.component import adapter
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from persistent.mapping import PersistentMapping

_marker = object()

"""
This entire module might benefit from being extracted into its own
package, perhaps at the collective namespace (collective.pmad, for
PersistentMapping Annotation Decorator).
"""


def to_key(prefix, name):
    return prefix + '.' + name


def _setup_dict_annotation(context, key):
    annotations = IAnnotations(context)
    if key not in annotations:
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


def annotator(iface, _key=None):
    """
    A class decorator to a class to turn it into an annotation that
    appends a new ``PersistentMapping`` within the annotatable only when
    an attribute is assigned for the first time, i.e. no automatic
    writes on initial adaptation from context.

    This works like a factory that will first take an interface, which
    it will then be the implementer interface for the class which this
    decorates.  This new class is able to adapt any IAnnotatable to
    return an object that behaves exactly like the initial class, with
    the attributes presented in the interface be automatically stored
    into the underlying mapping without the entire class construct.

    An ``uninstall`` classmethod is also provided which will remove the
    PersistentMapping identified by key.

    Naturally, the class can contain ``FieldProperty`` properties that
    are based on the interface schema that is about to be implemented by
    this.
    """

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

        classImplements(class_, iface)
        class_ = adapter(IAnnotatable)(class_)

        old_init = getattr(class_, '__init__')
        old_setattr = getattr(class_, '__setattr__')

        def __init__(self, context, *a, **kw):
            annotations = IAnnotations(context)
            d = annotations.get(key, _marker)

            if d is _marker:
                d = {}  # to let the loading routine work.
            elif not isinstance(d, PersistentMapping):
                raise TypeError(
                    'Could not instantiate a `%s` from %s with Annotation '
                    '`%s` as it is not of type PersistentMapping' % (
                        classname, context, key))

            for name in names:
                value = d.get(name, _marker)
                if value is _marker:
                    # if instance already has this attribute defined,
                    # do nothing.
                    if hasattr(self, name):
                        continue

                # set the loaded value to the instance only.
                try:
                    old_setattr(self, name, d.get(name))
                except WrongType as e:
                    raise TypeError(
                        'Could not assign attribute `%s` to class `%s` '
                        'with value from Annotation `%s` due to `%s`.' %
                        (name, classname, key, e.__repr__()))

            # finally associate context to the instance.
            old_setattr(self, 'context', context)
            old_init(self, *a, **kw)

        def __setattr__(self, name, value):
            """
            Whenever an attribute is set, persist it into the
            underyling PersistentMapping.
            """

            old_setattr(self, name, value)

            if name not in names:
                return

            d = _setup_dict_annotation(self.context, key)
            d[name] = value

        # TODO make the removal feature not an instance method
        # within every class?

        def uninstall(self):
            """
            Completely removes the annotation from context.
            """

            return _teardown_dict_annotation(self.context, key)

        # bind the modified methods to the input class

        class_.__init__ = MethodType(__init__, None, class_)
        class_.__setattr__ = MethodType(__setattr__, None, class_)
        class_.uninstall = MethodType(uninstall, None, class_)

        return class_

    return decorator
