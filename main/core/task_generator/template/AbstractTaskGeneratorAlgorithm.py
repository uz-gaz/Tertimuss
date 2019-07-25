import abc
from typing import Dict, List

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask


class AbstractTaskGeneratorAlgorithm(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def generate(self, options: Dict[str, str]) -> List[PeriodicTask]:
        pass
