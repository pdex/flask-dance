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


