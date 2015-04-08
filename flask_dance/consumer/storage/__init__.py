import six
from abc import ABCMeta, abstractmethod


class BaseTokenStorage(six.with_metaclass(ABCMeta)):
    @abstractmethod
    def __get__(self, blueprint):
        return None

    @abstractmethod
    def __set__(self, blueprint, token):
        return None

    @abstractmethod
    def __delete__(self, blueprint):
        return None


class NullStorage(BaseTokenStorage):
    """
    Don't actually store anything
    """
    def __get__(self, blueprint):
        return None
    def __set__(self, blueprint, token):
        return None
    def __delete__(self, blueprint):
        return None


class MemoryStorage(BaseTokenStorage):
    """
    "Store" the token in memory
    """
    def __init__(self, token=None, *args, **kwargs):
        self.token = token

    def __get__(self, blueprint):
        return self.token

    def __set__(self, blueprint, token):
        self.token = token

    def __delete__(self, blueprint):
        self.token = None
