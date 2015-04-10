from __future__ import unicode_literals
import functools
from collections import MutableMapping


class FakeCache(object):
    """
    An object that mimics just enough of Flask-Cache's API to be compatible
    with our needs, but does nothing.
    """
    def get(self, key):
        return None
    def set(self, key, value):
        return None
    def delete(self, key):
        return None


def first(iterable, default=None, key=None):
    """
    Return the first truthy value of an iterable.
    Shamelessly stolen from https://github.com/hynek/first
    """
    if key is None:
        for el in iterable:
            if el:
                return el
    else:
        for el in iterable:
            if key(el):
                return el
    return default


sentinel = object()

def getattrd(obj, name, default=sentinel):
    """
    Same as getattr(), but allows dot notation lookup
    Source: http://stackoverflow.com/a/14324459
    """
    try:
        return functools.reduce(getattr, name.split("."), obj)
    except AttributeError as e:
        if default is not sentinel:
            return default
        raise

class Dictective(object, MutableMapping):
    """
    A transparent proxy to a dict that detects changes, and runs a ``changed``
    method automatically when the dict is changed.
    """
    def __init__(self, func, dict=None):
        self._dict = dict or {}
        self.func = func

    def __getitem__(self, key):
        return self._dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        self._dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        self._dict.__delitem__(self, key)
        self.changed()

    def __len__(self):
        return self._dict.__len__(self)

    def __iter__(self):
        return self._dict.__iter__(self)

    def __repr__(self):
        return "{name}(dict={dict})".format(
            name=self.__class__.__name__, dict=self._dict,
        )

    def setdefault(self, key, value):
        result = self._dict.setdefault(self, key, value)
        self.changed()
        return result

    def update(self, *a, **kw):
        self._dict.update(self, *a, **kw)
        self.changed()

    def clear(self):
        self._dict.clear(self)
        self.changed()

    def changed(self):
        self.func(self._dict)
