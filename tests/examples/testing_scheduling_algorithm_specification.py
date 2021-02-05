import unittest
from typing import Dict, Optional, Set, List, Tuple

from tertimuss.simulation_lib.schedulers_definition import CentralizedAbstractScheduler
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationOptionsSpecification
from tertimuss.simulation_lib.system_definition import ProcessorDefinition, EnvironmentSpecification, TaskSet, \
    PeriodicTask, PreemptiveExecution, Criticality, Job, AperiodicTask
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification


class _SimpleGlobalEarliestDeadlineFirstScheduler(CentralizedAbstractScheduler):
    def __init__(self):
        """
        Create a simple global EDF scheduler instance
        """
        super().__init__(False)
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

        # All tasks will be executed
        tasks_to_execute = {k: i for (i, j), k in zip(tasks_that_can_be_executed, range(self.__m))}

        return tasks_to_execute, None, None

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


class SchedulingAlgorithmSpecificationTest(unittest.TestCase):
    @staticmethod
    def __create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                      period: float) -> PeriodicTask:
        # Create implicit deadline task with priority equal to identification id
        return PeriodicTask(identification=task_id,
                            worst_case_execution_time=worst_case_execution_time,
                            relative_deadline=period,
                            best_case_execution_time=None,
                            execution_time_distribution=None,
                            memory_footprint=None,
                            priority=None,
                            preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                            deadline_criteria=Criticality.HARD,
                            energy_consumption=None,
                            phase=None,
                            period=period)

    def test_simple_simulation_periodic_task_set(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(0, 10000, 20.0),
            self.__create_implicit_deadline_periodic_task_h_rt(1, 5000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 7000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(3, 7000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(4, 7000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(5, 14000, 20.0),
            self.__create_implicit_deadline_periodic_task_h_rt(6, 3000, 5.0)
        ]

        number_of_cores = 5
        available_frequencies = {1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
            scheduler=_SimpleGlobalEarliestDeadlineFirstScheduler()
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None
