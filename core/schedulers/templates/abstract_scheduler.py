import abc
from typing import Optional

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from output_generation.abstract_progress_bar import AbstractProgressBar


class SchedulerResult(object):
    def __init__(self, temperature_map: scipy.ndarray, max_temperature_cores: scipy.ndarray,
                 time_scheduler: scipy.ndarray, time_tcpn: scipy.ndarray,
                 execution_time_scheduler: scipy.ndarray, execution_time_tcpn: scipy.ndarray,
                 scheduler_assignation: scipy.ndarray,
                 frequencies: scipy.ndarray,
                 quantum: float):
        self.temperature_map = temperature_map
        self.max_temperature_cores = max_temperature_cores
        self.time_scheduler = time_scheduler
        self.time_tcpn = time_tcpn
        self.execution_time_scheduler = execution_time_scheduler
        self.execution_time_tcpn = execution_time_tcpn
        self.scheduler_assignation = scheduler_assignation
        self.frequencies = frequencies
        self.quantum = quantum


class AbstractScheduler(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def simulate(self, global_specification: GlobalSpecification,
                 global_model: GlobalModel, progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:
        pass
