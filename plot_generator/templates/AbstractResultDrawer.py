import abc
from typing import Dict

from core.problem_specification.GlobalSpecification import GlobalSpecification
from core.schedulers.templates.abstract_scheduler import SchedulerResult


class AbstractResultDrawer(object, metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def plot(cls, global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
             options: Dict[str, str]):
        """
        Plot results
        :param global_specification: Problem global specification
        :param scheduler_result: Result of the simulation
        :param options: Result drawer options
        """
        pass
