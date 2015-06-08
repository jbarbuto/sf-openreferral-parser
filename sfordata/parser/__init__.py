import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseParser(object):
    @abc.abstractmethod
    def parse(self, data):
        pass
