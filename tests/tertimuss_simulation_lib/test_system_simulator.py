import unittest
from typing import Set, Dict, Optional, Tuple, List

from matplotlib import animation

from tertimuss.simulation_lib.schedulers_definition import CentralizedScheduler
from tertimuss.simulation_lib.simulator import SimulationConfiguration, \
    JobSectionExecution, CPUUsedFrequency, \
    execute_scheduler_simulation, execute_scheduler_simulation_simple
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, \
    Environment, Processor, Job, TaskSet
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification
from tertimuss.visualization import generate_component_hotspots_plot, generate_board_temperature_evolution_2d_video


class SystemSimulatorTest(unittest.TestCase):

    @staticmethod
    def __simple_priority_scheduler_definition() -> CentralizedScheduler:
        # This scheduler will do the schedule based on the priority given by te user to each task
        class SimplePriorityScheduler(CentralizedScheduler):
            def __init__(self):
                super().__init__(True)
                self.__m = 0
                self.__tasks_priority: Dict[int, int] = {}
                self.__active_jobs_priority: Dict[int, int] = {}

            def check_schedulability(self, cpu_specification: Processor,
                                     environment_specification: Environment, task_set: TaskSet) \
                    -> [bool, Optional[str]]:
                is_schedulable = all((i.priority is not None for i in task_set.periodic_tasks)) and all(
                    (i.priority is not None for i in task_set.aperiodic_tasks)) and all(
                    (i.priority is not None for i in task_set.sporadic_tasks))

                return is_schedulable, None if is_schedulable else "All task must have priority"

            def offline_stage(self, cpu_specification: Processor,
                              environment_specification: Environment, task_set: TaskSet) -> int:
                self.__m = len(cpu_specification.cores_definition)

                self.__tasks_priority = {i.identifier: i.priority for i in task_set.periodic_tasks +
                                         task_set.aperiodic_tasks + task_set.sporadic_tasks}

                clock_available_frequencies = Set.intersection(*[i.core_type.available_frequencies for i
                                                                 in cpu_specification.cores_definition.values()])

                return max(clock_available_frequencies)

            def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                                jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                                cores_max_temperature: Optional[Dict[int, float]]) \
                    -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
                tasks_to_execute = sorted(self.__active_jobs_priority.items(), key=lambda j: j[1], reverse=True)
                return {j: i for (i, _), j in zip(tasks_to_execute, range(self.__m))}, None, None

            def on_major_cycle_start(self, global_time: float) -> bool:
                return True

            def on_jobs_activation(self, global_time: float, activation_time: float,
                                   jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
                self.__active_jobs_priority.update({i: self.__tasks_priority[j] for i, j in jobs_id_tasks_ids})
                return True

            def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
                for i in jobs_id:
                    del self.__active_jobs_priority[i]
                return True

            def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
                for i in jobs_id:
                    del self.__active_jobs_priority[i]
                return True

        return SimplePriorityScheduler()

    @staticmethod
    def __bad_behaviour_scheduler_definition() -> CentralizedScheduler:
        # This scheduler will do the schedule based on the priority given by te user to each task
        class SchedulerWithBadBehaviour(CentralizedScheduler):
            def __init__(self):
                super().__init__(True)

            def check_schedulability(self, cpu_specification: Processor,
                                     environment_specification: Environment, task_set: TaskSet) \
                    -> [bool, Optional[str]]:
                return True, None

            def offline_stage(self, cpu_specification: Processor,
                              environment_specification: Environment, task_set: TaskSet) -> int:
                clock_available_frequencies = Set.intersection(*[i.core_type.available_frequencies for i
                                                                 in cpu_specification.cores_definition.values()])

                return max(clock_available_frequencies)

            def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                                jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                                cores_max_temperature: Optional[Dict[int, float]]) \
                    -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
                return {0: -1}, None, None

            def on_major_cycle_start(self, global_time: float) -> bool:
                return True

        return SchedulerWithBadBehaviour()

    @staticmethod
    def __parallel_scheduler_definition() -> CentralizedScheduler:
        # This is a non-preemptive scheduler which will assign each job to all the available CPUs using the FIFO philosophy
        class ParallelScheduler(CentralizedScheduler):
            def __init__(self):
                super().__init__(True)
                self.__m = 0
                self.__tasks_wcet: Dict[int, int] = []
                # FIFO queue of active jobs (pairs of job identifier and job execution time)
                self.__jobs_queue: List[Tuple[int, int]] = []
                # Next calculated scheduling point in global time
                self.__next_scheduling_point = 0.0

            def check_schedulability(self, cpu_specification: Processor,
                                     environment_specification: Environment, task_set: TaskSet) \
                    -> [bool, Optional[str]]:
                self.__m = len(cpu_specification.cores_definition)
                is_schedulable = all((i.worst_case_execution_time % self.__m == 0 for i in task_set.tasks()))
                return is_schedulable, None if is_schedulable else "All WCET must be exactly divisible by the number of cores"

            def offline_stage(self, cpu_specification: Processor,
                              environment_specification: Environment, task_set: TaskSet) -> int:
                self.__tasks_wcet = {task.identifier: task.worst_case_execution_time for task in task_set.tasks()}
                clock_available_frequencies = Set.intersection(*[i.core_type.available_frequencies for i
                                                                 in cpu_specification.cores_definition.values()])
                return max(clock_available_frequencies)

            def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                                jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                                cores_max_temperature: Optional[Dict[int, float]]) \
                    -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
                jobs_to_cpu_assignation, cycles_to_sleep = None, None
                planned_scheduling_point = global_time >= self.__next_scheduling_point
                if planned_scheduling_point:
                    # Next job in the queue is executed because the CPUs are left empty
                    next_job_id, next_job_exec_time = self.__jobs_queue.pop(0) if len(self.__jobs_queue) != 0 else (None, None)
                    self.__next_scheduling_point = global_time + next_job_exec_time / cores_frequency
                    jobs_to_cpu_assignation = {i: next_job_id for i in range(self.__m)} if next_job_id is not None else {}
                    cycles_to_sleep = next_job_exec_time  # if len(self.__jobs_queue) != 0 else None
                else:
                    # Recently activated jobs execution is deferred because CPUs are currently busy with another job
                    jobs_to_cpu_assignation = jobs_being_executed_id
                    cycles_to_sleep = int((self.__next_scheduling_point - global_time) * cores_frequency)
                if self.is_debug:
                    self.__print_scheduling_point(global_time, planned_scheduling_point, jobs_to_cpu_assignation,
                                                  cycles_to_sleep, active_jobs_id)
                return jobs_to_cpu_assignation, cycles_to_sleep, None

            def on_major_cycle_start(self, global_time: float) -> bool:
                return False

            def on_jobs_activation(self, global_time: float, activation_time: float,
                                   jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
                self.__jobs_queue += [(job, self.__tasks_wcet[task] // self.__m) for job, task in jobs_id_tasks_ids]
                if self.is_debug:
                    self.__print_activated_jobs(global_time, jobs_id_tasks_ids)
                return True

            def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
                return False

            def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
                return False

            def __print_scheduling_point(self, global_time: float, planned: bool, jobs_to_cpu_assignation: Dict[int, int],
                                         cycles_to_sleep: int, active_jobs_id: Set[int]):
                print(global_time, "Scheduling point", "" if planned else "(deferred)")
                print("\tJobs to CPU assignation", jobs_to_cpu_assignation)
                print("\tCycles to sleep", cycles_to_sleep)
                print("\tNext scheduling point", self.__next_scheduling_point)
                print("\tActive jobs", active_jobs_id)
                print("\tJobs queue:", ["job " + str(job_id) for job_id, _ in self.__jobs_queue])

            def __print_activated_jobs(self, global_time: float, jobs_id_tasks_ids: List[Tuple[int, int]]):
                print(global_time, "Jobs activation")
                print("\tJobs activated", ["job " + str(job) + " (task " + str(task) + ")"
                                           for job, task in jobs_id_tasks_ids])
                print("\tJobs queue:", ["job " + str(job_id) for job_id, _ in self.__jobs_queue])

        return ParallelScheduler()

    @staticmethod
    def __create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                      period: float, priority: Optional[int]) -> PeriodicTask:
        # Create implicit deadline task with priority equal to identification id
        return PeriodicTask(identifier=task_id,
                            worst_case_execution_time=worst_case_execution_time,
                            relative_deadline=period,
                            best_case_execution_time=None,
                            execution_time_distribution=None,
                            memory_footprint=None,
                            priority=priority,
                            preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                            deadline_criteria=Criticality.HARD,
                            energy_consumption=None,
                            phase=None,
                            period=period)

    def test_simple_simulation_periodic_task_set(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(3, 3000, 7.0, 3),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 7.0, 2),
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 14.0, 1),
            self.__create_implicit_deadline_periodic_task_h_rt(0, 3000, 14.0, 0)
        ]

        jobs_list = [
            # Task 3
            Job(identifier=0, activation_time=0.0, task=periodic_tasks[0]),
            Job(identifier=1, activation_time=7.0, task=periodic_tasks[0]),

            # Task 2
            Job(identifier=2, activation_time=0.0, task=periodic_tasks[1]),
            Job(identifier=3, activation_time=7.0, task=periodic_tasks[1]),

            # Task 1
            Job(identifier=4, activation_time=0.0, task=periodic_tasks[2]),

            # Task 0
            Job(identifier=5, activation_time=0.0, task=periodic_tasks[3]),
        ]

        number_of_cores = 2
        available_frequencies = {1000}

        simulation_result = execute_scheduler_simulation(
            simulation_start_time=0.0,
            simulation_end_time=14.0,
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            jobs=jobs_list,
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=self.__simple_priority_scheduler_definition()
        )

        # Correct execution
        correct_job_sections_execution = {
            0: [
                JobSectionExecution(job_id=0, task_id=3, execution_start_time=0.0, execution_end_time=3.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=2, task_id=2, execution_start_time=3.0, execution_end_time=4.0,
                                    number_of_executed_cycles=1000),
                JobSectionExecution(job_id=4, task_id=1, execution_start_time=4.0, execution_end_time=7.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=1, task_id=3, execution_start_time=7.0, execution_end_time=10.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=3, task_id=2, execution_start_time=10.0, execution_end_time=11.0,
                                    number_of_executed_cycles=1000)],
            1: [
                JobSectionExecution(job_id=2, task_id=2, execution_start_time=0.0, execution_end_time=3.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=4, task_id=1, execution_start_time=3.0, execution_end_time=4.0,
                                    number_of_executed_cycles=1000),
                JobSectionExecution(job_id=5, task_id=0, execution_start_time=4.0, execution_end_time=7.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=3, task_id=2, execution_start_time=7.0, execution_end_time=10.0,
                                    number_of_executed_cycles=3000)]
        }

        correct_cpu_frequencies = {0: [CPUUsedFrequency(1000, 0.0, 14.0)], 1: [CPUUsedFrequency(1000, 0.0, 14.0)]}

        correct_scheduling_points = [0.0, 3.0, 4.0, 7.0, 10.0]

        assert simulation_result.have_been_scheduled

        assert (simulation_result.job_sections_execution == correct_job_sections_execution)

        assert (simulation_result.cpus_frequencies == correct_cpu_frequencies)

        assert (simulation_result.scheduling_points == correct_scheduling_points)

        assert (simulation_result.hard_real_time_deadline_missed_stack_trace is None)

    def test_simple_simulation_periodic_task_set_hard_rt_miss(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 7.0, 1),
            self.__create_implicit_deadline_periodic_task_h_rt(0, 4000, 7.0, 0),
            self.__create_implicit_deadline_periodic_task_h_rt(3, 4000, 14.0, 3),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 14.0, 2)
        ]

        number_of_cores = 2
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
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=self.__simple_priority_scheduler_definition()
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert (simulation_result.hard_real_time_deadline_missed_stack_trace is not None
                and simulation_result.hard_real_time_deadline_missed_stack_trace.time == 7.0)

    def test_simple_simulation_bad_behaviour_scheduler(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 7.0, 1),
            self.__create_implicit_deadline_periodic_task_h_rt(0, 4000, 7.0, 0),
            self.__create_implicit_deadline_periodic_task_h_rt(3, 4000, 14.0, 3),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 14.0, 2)
        ]

        number_of_cores = 2
        available_frequencies = {1000}

        try:
            execute_scheduler_simulation_simple(
                tasks=TaskSet(
                    periodic_tasks=periodic_tasks,
                    aperiodic_tasks=[],
                    sporadic_tasks=[]
                ),
                aperiodic_tasks_jobs=[],
                sporadic_tasks_jobs=[],
                processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
                environment_specification=default_environment_specification(),
                simulation_options=SimulationConfiguration(id_debug=True),
                scheduler=self.__bad_behaviour_scheduler_definition()
            )
            assert False
        except Exception:
            assert True

    def test_simple_simulation_not_accepted_task_set(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 7.0, 1),
            self.__create_implicit_deadline_periodic_task_h_rt(0, 4000, 7.0, 0),
            self.__create_implicit_deadline_periodic_task_h_rt(3, 4000, 14.0, 3),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 14.0, None)
        ]

        number_of_cores = 2
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
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=self.__simple_priority_scheduler_definition()
        )

        # Correct execution
        assert not simulation_result.have_been_scheduled

    def test_simple_simulation_periodic_task_set_with_thermal(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(3, 3000, 7.0, 3),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 7.0, 2),
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 14.0, 1),
            self.__create_implicit_deadline_periodic_task_h_rt(0, 3000, 14.0, 0)
        ]

        jobs_list = [
            # Task 3
            Job(identifier=0, activation_time=0.0, task=periodic_tasks[0]),
            Job(identifier=1, activation_time=7.0, task=periodic_tasks[0]),

            # Task 2
            Job(identifier=2, activation_time=0.0, task=periodic_tasks[1]),
            Job(identifier=3, activation_time=7.0, task=periodic_tasks[1]),

            # Task 1
            Job(identifier=4, activation_time=0.0, task=periodic_tasks[2]),

            # Task 0
            Job(identifier=5, activation_time=0.0, task=periodic_tasks[3]),
        ]

        number_of_cores = 2
        available_frequencies = {1000}

        simulation_result = execute_scheduler_simulation(
            simulation_start_time=0.0,
            simulation_end_time=14.0,
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            jobs=jobs_list,
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, thermal_simulation_type="DVFS",
                                                       simulate_thermal_behaviour=True),
            scheduler=self.__simple_priority_scheduler_definition()
        )

        # Correct execution
        correct_job_sections_execution = {
            0: [
                JobSectionExecution(job_id=0, task_id=3, execution_start_time=0.0, execution_end_time=3.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=2, task_id=2, execution_start_time=3.0, execution_end_time=4.0,
                                    number_of_executed_cycles=1000),
                JobSectionExecution(job_id=4, task_id=1, execution_start_time=4.0, execution_end_time=7.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=1, task_id=3, execution_start_time=7.0, execution_end_time=10.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=3, task_id=2, execution_start_time=10.0, execution_end_time=11.0,
                                    number_of_executed_cycles=1000)],
            1: [
                JobSectionExecution(job_id=2, task_id=2, execution_start_time=0.0, execution_end_time=3.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=4, task_id=1, execution_start_time=3.0, execution_end_time=4.0,
                                    number_of_executed_cycles=1000),
                JobSectionExecution(job_id=5, task_id=0, execution_start_time=4.0, execution_end_time=7.0,
                                    number_of_executed_cycles=3000),
                JobSectionExecution(job_id=3, task_id=2, execution_start_time=7.0, execution_end_time=10.0,
                                    number_of_executed_cycles=3000)]
        }

        correct_cpu_frequencies = {0: [CPUUsedFrequency(1000, 0.0, 14.0)], 1: [CPUUsedFrequency(1000, 0.0, 14.0)]}

        correct_scheduling_points = [0.0, 3.0, 4.0, 7.0, 10.0]

        assert simulation_result.have_been_scheduled

        assert (simulation_result.job_sections_execution == correct_job_sections_execution)

        assert (simulation_result.cpus_frequencies == correct_cpu_frequencies)

        assert (simulation_result.scheduling_points == correct_scheduling_points)

        assert (simulation_result.hard_real_time_deadline_missed_stack_trace is None)

    def test_simulation_nonparallelization_check(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 7.0, 1),
            self.__create_implicit_deadline_periodic_task_h_rt(0, 4000, 7.0, 0),
            self.__create_implicit_deadline_periodic_task_h_rt(3, 4000, 14.0, 3),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 14.0, 2)
        ]

        jobs_list = [
            # Task 1
            Job(identifier=0, activation_time=0.0, task=periodic_tasks[0]),
            Job(identifier=1, activation_time=7.0, task=periodic_tasks[0]),

            # Task 0
            Job(identifier=2, activation_time=0.0, task=periodic_tasks[1]),
            Job(identifier=3, activation_time=7.0, task=periodic_tasks[1]),

            # Task 3
            Job(identifier=4, activation_time=0.0, task=periodic_tasks[2]),

            # Task 2
            Job(identifier=5, activation_time=0.0, task=periodic_tasks[3]),
        ]

        number_of_cores = 2
        available_frequencies = {1000}

        simulation_result = execute_scheduler_simulation(
            simulation_start_time=0.0,
            simulation_end_time=14.0,
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            jobs=jobs_list,
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=self.__parallel_scheduler_definition()
        )

        # Correct execution
        correct_job_sections_execution = {
            0: [
                JobSectionExecution(job_id=0, task_id=1, execution_start_time=0.0, execution_end_time=2.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=2, task_id=0, execution_start_time=2.0, execution_end_time=4.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=4, task_id=3, execution_start_time=4.0, execution_end_time=6.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=5, task_id=2, execution_start_time=6.0, execution_end_time=8.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=1, task_id=1, execution_start_time=8.0, execution_end_time=10.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=3, task_id=0, execution_start_time=10.0, execution_end_time=12.0,
                                    number_of_executed_cycles=4000)],
            1: [
                JobSectionExecution(job_id=0, task_id=1, execution_start_time=0.0, execution_end_time=2.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=2, task_id=0, execution_start_time=2.0, execution_end_time=4.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=4, task_id=3, execution_start_time=4.0, execution_end_time=6.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=5, task_id=2, execution_start_time=6.0, execution_end_time=8.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=1, task_id=1, execution_start_time=8.0, execution_end_time=10.0,
                                    number_of_executed_cycles=4000),
                JobSectionExecution(job_id=3, task_id=0, execution_start_time=10.0, execution_end_time=12.0,
                                    number_of_executed_cycles=4000)]
        }

        correct_cpu_frequencies = {0: [CPUUsedFrequency(1000, 0.0, 14.0)], 1: [CPUUsedFrequency(1000, 0.0, 14.0)]}

        correct_scheduling_points = [0.0, 2.0, 4.0, 6.0, 7.0, 8.0, 10.0]

        assert simulation_result.have_been_scheduled

        assert (simulation_result.job_sections_execution == correct_job_sections_execution)

        assert (simulation_result.cpus_frequencies == correct_cpu_frequencies)

        assert (simulation_result.scheduling_points == correct_scheduling_points)

        assert (simulation_result.hard_real_time_deadline_missed_stack_trace is None)

        # Faulty execution
        try:
            execute_scheduler_simulation(
                simulation_start_time=0.0,
                simulation_end_time=14.0,
                tasks=TaskSet(
                    periodic_tasks=periodic_tasks,
                    aperiodic_tasks=[],
                    sporadic_tasks=[]
                ),
                jobs=jobs_list,
                processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
                environment_specification=default_environment_specification(),
                simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
                scheduler=self.__parallel_scheduler_definition()
            )
            assert False
        except Exception:
            assert True
