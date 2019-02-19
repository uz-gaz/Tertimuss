import abc


class TaskGeneratorAlgorithm(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate(self) -> list:
        pass
