import abc
from typing import Dict


class AbstractTaskGeneratorAlgorithm(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate(self, options: Dict[str, str]) -> list:
        pass
