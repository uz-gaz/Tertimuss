import abc
from typing import Optional

from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
from main.core.tcpn_model_generator.global_model import GlobalModel
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.ui.common.abstract_progress_bar import AbstractProgressBar


class AbstractScheduler(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def simulate(self, global_specification: GlobalSpecification,
                 global_model: GlobalModel, progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:
        pass
