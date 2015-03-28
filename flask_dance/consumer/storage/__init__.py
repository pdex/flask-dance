import six
from abc import ABCMeta, abstractmethod


class BaseTokenStorage(six.with_metaclass(ABCMeta)):
    def __init__(self, blueprint, *args, **kwargs):
        self.blueprint = blueprint

    @abstractmethod
    def get(self):
        return None

    @abstractmethod
    def set(self, token):
        return None

    @abstractmethod
    def delete(self):
        return None


class NullStorage(BaseTokenStorage):
    """
    Don't actually store anything
    """
    def get(self):
        return None
    def set(self, token):
        return None
    def delete(self):
        return None


class MemoryStorage(BaseTokenStorage):
    """
    "Store" the token in memory
    """
    def __init__(self, blueprint, token=None, *args, **kwargs):
        super(MemoryStorage, self).__init__(blueprint, *args, **kwargs)
        self.token = token

    def get(self):
        return self.token

    def set(self, token):
        self.token = token

    def delete(self):
        self.token = None
