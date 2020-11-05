import abc

from ..system_definition import HomogeneousCpuSpecification, TaskSet, EnvironmentSpecification

from typing import Optional, Set, Dict, Tuple, Union, List


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
    def check_schedulability(self, cpu_specification: Union[HomogeneousCpuSpecification],
                             environment_specification: EnvironmentSpecification,
                             task_set: TaskSet) -> [bool, Optional[str]]:
        """
        Return true if the scheduler can be able to schedule the system. In negative case, it can return a reason.
        In example, an scheduler that only can work with periodic tasks with phase=0, can return
         [false, "Only can schedule tasks with phase=0"]

        :param environment_specification: Specification of the environment
        :param cpu_specification: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        pass

    @abc.abstractmethod
    def offline_stage(self, cpu_specification: Union[HomogeneousCpuSpecification],
                      environment_specification: EnvironmentSpecification,
                      task_set: TaskSet) -> int:
        """
        Method to implement with the offline stage scheduler tasks

        :param environment_specification: Specification of the environment
        :param cpu_specification: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        pass

    @abc.abstractmethod
    def schedule_policy(self, global_time: float, time_since_major_cycle_start: float,
                        active_jobs_id: Set[int], jobs_being_executed_id: Dict[int, int],
                        cores_frequency: int, cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police

        :param time_since_major_cycle_start: Time in seconds since the major cycle starts
        :param global_time: Time in seconds since the simulation starts
        :param jobs_being_executed_id: Ids of the jobs that are currently executed on the system. The dictionary has as
         key the CPU id, and as value the job id.
        :param active_jobs_id: Identifications of the jobs that are currently active
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
    def on_major_cycle_start(self, global_time: float) -> bool:
        """
        On new major cycle start event

        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return True

    def on_jobs_activation(self, global_time: float, activation_time: float, jobs_id_tasks_ids: List[Tuple[int, int]]) \
            -> bool:
        """
        Method to implement with the actual on job activation scheduler police.
        This method is the recommended place to detect the arrival of an aperiodic or sporadic task.

        :param jobs_id_tasks_ids: List[Identification of the task which job have been activated,
        Identification of the job that have been activated]
        :param global_time: Actual time in seconds since the simulation starts
        :param activation_time: Time where the activation was produced (It can be different from the global_time in the
         case that it doesn't adjust to a cycle end)
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return False

    def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police

        :param jobs_id: Identification of the jobs that have missed the deadline
        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return False

    def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police

        :param jobs_id: Identification of the job that have finished its execution
        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return False
