import abc


class AbstractTaskGeneratorAlgorithm(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate(self) -> list:
        pass
