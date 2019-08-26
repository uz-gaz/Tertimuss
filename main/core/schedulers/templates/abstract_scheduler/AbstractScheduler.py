import abc
from typing import Optional

from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
from main.core.tcpn_model_generator.GlobalModel import GlobalModel
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.ui.common.AbstractProgressBar import AbstractProgressBar


class AbstractScheduler(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def simulate(self, global_specification: GlobalSpecification,
                 global_model: GlobalModel, progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:
        """
        Simulate problem
        :param global_specification: global specification of the problem
        :param global_model: global TCPN model
        :param progress_bar: progress bar object if want to get simulation state feedback
        :return:
        """
        pass
