"""
================================================
Global Earliest Deadline First Scheduler (G-EDF)
================================================

This module provides the following class:
- :class:`GEDFScheduler`
"""

from typing import Dict, Optional, Set, List, Tuple

from ..simulation_lib.schedulers_definition import CentralizedAbstractScheduler
from ..simulation_lib.system_definition import ProcessorDefinition, EnvironmentSpecification, TaskSet


class GEDFScheduler(CentralizedAbstractScheduler):
    """
    Implements the Global Earliest Deadline First Scheduler (G-EDF)
    """

    def __init__(self, activate_debug: bool):
        """
        Create a global EDF scheduler instance
        :param activate_debug:  True if want to communicate the scheduler to be in debug mode
        """
        super().__init__(activate_debug)
        self.__m = 0
        self.__tasks_relative_deadline: Dict[int, float] = {}
        self.__active_jobs_priority: Dict[int, float] = {}

    def check_schedulability(self, processor_definition: ProcessorDefinition,
                             environment_specification: EnvironmentSpecification, task_set: TaskSet) \
            -> [bool, Optional[str]]:
        """
        Return true if the scheduler can be able to schedule the system. In negative case, it can return a reason.
        In example, an scheduler that only can work with periodic tasks with phase=0, can return
         [false, "Only can schedule tasks with phase=0"]

        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        return True, None

    def offline_stage(self, processor_definition: ProcessorDefinition,
                      environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
        """
          Method to implement with the offline stage scheduler tasks

          :param environment_specification: Specification of the environment
          :param processor_definition: Specification of the cpu
          :param task_set: Tasks in the system
          :return CPU frequency
          """
        m = len(processor_definition.cores_definition)

        clock_available_frequencies = Set.intersection(*[i.core_type.available_frequencies for i
                                                         in processor_definition.cores_definition.values()])

        self.__m = m

        self.__tasks_relative_deadline = {i.identifier: i.relative_deadline for i in
                                          task_set.periodic_tasks + task_set.aperiodic_tasks +
                                          task_set.sporadic_tasks}

        return max(clock_available_frequencies)

    def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                        jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                        cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police

        :param global_time: Time in seconds since the simulation starts
        :param jobs_being_executed_id: Ids of the jobs that are currently executed on the system. The dictionary has as
         key the CPU id (it goes from 0 to number of CPUs - 1), and as value the job id.
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
        # The priority of the tasks must be inverse to the deadline
        tasks_that_can_be_executed: List[Tuple[int, float]] = sorted([i for i in self.__active_jobs_priority.items()],
                                                                     key=lambda j: j[1])

        if len(tasks_that_can_be_executed) <= self.__m:
            # All tasks will be executed
            tasks_to_execute = [i for (i, j) in tasks_that_can_be_executed]
        else:
            # Tasks that will be executed because have height priority
            tasks_to_execute_height_priority = [i for (i, j) in tasks_that_can_be_executed if
                                                j < tasks_that_can_be_executed[self.__m - 1][1]]

            # Tasks with middle priority to execute
            tasks_to_execute_middle_priority = [i for (i, j) in tasks_that_can_be_executed if
                                                j == tasks_that_can_be_executed[self.__m - 1][
                                                    1] and i in jobs_being_executed_id.values()]

            # Tasks with lowest priority to execute
            tasks_to_execute_lowest_priority = [i for (i, j) in tasks_that_can_be_executed if
                                                j == tasks_that_can_be_executed[self.__m - 1][
                                                    1] and i not in jobs_being_executed_id.values()]

            if len(tasks_to_execute_height_priority) + len(tasks_to_execute_middle_priority) <= self.__m:
                tasks_to_execute = tasks_to_execute_height_priority + tasks_to_execute_middle_priority \
                                   + tasks_to_execute_lowest_priority[0: self.__m -
                                                                         (len(tasks_to_execute_height_priority) +
                                                                          len(tasks_to_execute_middle_priority))]
            else:
                tasks_to_execute = tasks_to_execute_height_priority + tasks_to_execute_middle_priority[
                                                                      0: self.__m - len(
                                                                          tasks_to_execute_height_priority)]

        # Do affinity to avoid preemptions (migrations not taking in count)
        jobs_running = {i: j for (i, j) in jobs_being_executed_id.items() if j in tasks_to_execute}

        remaining_tasks_to_execute = [i for i in tasks_to_execute if i not in jobs_running.values()]
        remaining_cpus = [i for i in range(self.__m) if i not in jobs_running.keys()]

        jobs_running.update({i: j for (i, j) in zip(remaining_cpus, remaining_tasks_to_execute)})

        return jobs_running, None, None

    def on_major_cycle_start(self, global_time: float) -> bool:
        """
        On new major cycle start event

        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        return True

    def on_jobs_activation(self, global_time: float, activation_time: float,
                           jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
        """
        Method to implement with the actual on job activation scheduler police.
        This method is the recommended place to detect the arrival of an aperiodic or sporadic task.

        :param jobs_id_tasks_ids: List[Identification of the job that have been activated,
         Identification of the task which job have been activated]
        :param global_time: Actual time in seconds since the simulation starts
        :param activation_time: Time where the activation was produced (It can be different from the global_time in the
         case that it doesn't adjust to a cycle end)
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        self.__active_jobs_priority.update(
            {i: self.__tasks_relative_deadline[j] + activation_time for i, j in jobs_id_tasks_ids})
        return True

    def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
        """
         Method to implement with the actual on aperiodic arrive scheduler police

         :param jobs_id: Identification of the jobs that have missed the deadline
         :param global_time: Time in seconds since the simulation starts
         :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
         """
        for i in jobs_id:
            del self.__active_jobs_priority[i]
        return True

    def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police

        :param jobs_id: Identification of the job that have finished its execution
        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        for i in jobs_id:
            del self.__active_jobs_priority[i]
        return True
