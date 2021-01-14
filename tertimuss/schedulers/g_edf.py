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

    def check_schedulability(self, cpu_specification: ProcessorDefinition,
                             environment_specification: EnvironmentSpecification, task_set: TaskSet) \
            -> [bool, Optional[str]]:
        return True, None

    def offline_stage(self, cpu_specification: ProcessorDefinition,
                      environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
        m = len(cpu_specification.cores_definition)

        clock_available_frequencies = Set.intersection(*[i.core_type.available_frequencies for i
                                                         in cpu_specification.cores_definition.values()])

        self.__m = m

        self.__tasks_relative_deadline = {i.identification: i.relative_deadline for i in
                                          task_set.periodic_tasks + task_set.aperiodic_tasks +
                                          task_set.sporadic_tasks}

        return max(clock_available_frequencies)

    def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                        jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                        cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:

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
        return True

    def on_jobs_activation(self, global_time: float, activation_time: float,
                           jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
        self.__active_jobs_priority.update(
            {i: self.__tasks_relative_deadline[j] + activation_time for i, j in jobs_id_tasks_ids})
        return True

    def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
        for i in jobs_id:
            del self.__active_jobs_priority[i]
        return True

    def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
        for i in jobs_id:
            del self.__active_jobs_priority[i]
        return True
