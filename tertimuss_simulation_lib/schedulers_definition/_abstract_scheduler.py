import abc

import numpy

from ..system_definition import CpuSpecification, TaskSet, EnvironmentSpecification, PeriodicTask

from typing import List, Optional, Set, Dict, Tuple


class CentralizedAbstractScheduler(object, metaclass=abc.ABCMeta):
    """
    Base centralized scheduler.
    It must be assume that the simulation always start in the beginning of a major cycle, but can take various major
    cycles or less than one
    """

    def __init__(self, activate_debug: bool):
        """
        Create the centralized scheduler
        :param activate_debug: True if want to communicate the scheduler to be in debug mode
        """
        self.is_debug = activate_debug

    @abc.abstractmethod
    def offline_stage(self, cpu_specification: CpuSpecification, environment_specification: EnvironmentSpecification,
                      periodic_tasks: Set[PeriodicTask]) -> int:
        """
        Method to implement with the offline stage scheduler tasks
        :param environment_specification: Specification of the environment
        :param cpu_specification: Specification of the cpu
        :param periodic_tasks: Periodic tasks in the system
        :return CPU frequency
        """
        pass

    @abc.abstractmethod
    def schedule_policy(self, global_time: float,
                        time_since_major_cycle_start: float,
                        cycles_executed_since_major_cycle_start: int,
                        active_jobs_id: Set[int],
                        jobs_being_executed_id: Dict[int, int],
                        cores_frequency: int, cores_max_temperature: Optional[Dict[int, float]]) -> \
            Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police
        :param cycles_executed_since_major_cycle_start: Cycles executed since the major cycle start
        :param time_since_major_cycle_start: Time in seconds since the major cycle starts
        :param global_time: Time in seconds since the simulation starts
        :param jobs_being_executed_id: Ids of the jobs that are currently executed on the system. The dictionary has as
         key the CPU id, and as value the job id.
        :param active_jobs_id: Ids of the jobs that are currently active
         (look in :ref:..system_definition.DeadlineCriteria for more info) and can be executed.
        :param cores_frequency: Frequencies of cores on the scheduler invocation in Hz.
        :param cores_max_temperature: Max temperature of each core. The dictionary has as
         key the CPU id, and as value the temperature in Kelvin degrees.
        :return: Tuple of [
         Jobs CPU assignation. The dictionary has as key the CPU id, and as value the job id,
         Cycles to execute until the next invocation of the scheduler. If None, it won't be executed until a system
         event trigger its invocation,
         CPU frequency. If None, it will maintain the last used frequency (cores_frequency)
        ]
        """
        pass

    #
    # System events
    #
    @abc.abstractmethod
    def on_major_cycle_start(self, global_time: float) -> bool:
        """
        On new major cycle start event
        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return True

    def on_aperiodic_arrive(self, global_time: float, ) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return False

    def on_job_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                      actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return False

    def on_job_deadline_missed(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                               actual_cores_frequency: List[int],
                               cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return False

    def on_job_execution_finished(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                                  actual_cores_frequency: List[int],
                                  cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return False
