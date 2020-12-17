import unittest
from typing import Set, Dict, Optional, Tuple, Union, List

from tertimuss.simulation_lib.simulator import TaskSet, SimulationOptionsSpecification, \
    CentralizedAbstractScheduler, JobSectionExecution, CPUUsedFrequency, Job, execute_simulation, \
    execute_simulation_major_cycle
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, \
    HomogeneousCpuSpecification, EnvironmentSpecification
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification


class SystemSimulatorTest(unittest.TestCase):

    @staticmethod
    def __simple_priority_scheduler_definition() -> CentralizedAbstractScheduler:
        # This scheduler will do the schedule based on the priority given by te user to each task
        class SimplePriorityScheduler(CentralizedAbstractScheduler):
            def __init__(self):
                super().__init__(True)
                self.__m = 0
                self.__tasks_priority: Dict[int, int] = {}
                self.__active_jobs_priority: Dict[int, int] = {}

            def check_schedulability(self, cpu_specification: Union[HomogeneousCpuSpecification],
                                     environment_specification: EnvironmentSpecification, task_set: TaskSet) \
                    -> [bool, Optional[str]]:
                is_schedulable = all((i.priority is not None for i in task_set.periodic_tasks)) and all(
                    (i.priority is not None for i in task_set.aperiodic_tasks)) and all(
                    (i.priority is not None for i in task_set.sporadic_tasks))

                return is_schedulable, None if is_schedulable else "All task must have priority"

            def offline_stage(self, cpu_specification: Union[HomogeneousCpuSpecification],
                              environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
                self.__m = cpu_specification.cores_specification.number_of_cores

                self.__tasks_priority = {i.identification: i.priority for i in
                                         task_set.periodic_tasks + task_set.aperiodic_tasks + task_set.sporadic_tasks}

                return max(cpu_specification.cores_specification.available_frequencies)

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
    def __bad_behaviour_scheduler_definition() -> CentralizedAbstractScheduler:
        # This scheduler will do the schedule based on the priority given by te user to each task
        class SchedulerWithBadBehaviour(CentralizedAbstractScheduler):
            def __init__(self):
                super().__init__(True)

            def check_schedulability(self, cpu_specification: Union[HomogeneousCpuSpecification],
                                     environment_specification: EnvironmentSpecification, task_set: TaskSet) \
                    -> [bool, Optional[str]]:
                return True, None

            def offline_stage(self, cpu_specification: Union[HomogeneousCpuSpecification],
                              environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
                return max(cpu_specification.cores_specification.available_frequencies)

            def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                                jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                                cores_max_temperature: Optional[Dict[int, float]]) \
                    -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
                return {0: -1}, None, None

            def on_major_cycle_start(self, global_time: float) -> bool:
                return True

        return SchedulerWithBadBehaviour()

    @staticmethod
    def __create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                      period: float, priority: Optional[int]) -> PeriodicTask:
        # Create implicit deadline task with priority equal to identification id
        return PeriodicTask(identification=task_id,
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
            Job(identification=0, activation_time=0.0, task=periodic_tasks[0]),
            Job(identification=1, activation_time=7.0, task=periodic_tasks[0]),

            # Task 2
            Job(identification=2, activation_time=0.0, task=periodic_tasks[1]),
            Job(identification=3, activation_time=7.0, task=periodic_tasks[1]),

            # Task 1
            Job(identification=4, activation_time=0.0, task=periodic_tasks[2]),

            # Task 0
            Job(identification=5, activation_time=0.0, task=periodic_tasks[3]),
        ]

        number_of_cores = 2
        available_frequencies = {1000}

        simulation_result = execute_simulation(
            simulation_start_time=0.0,
            simulation_end_time=14.0,
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            jobs=jobs_list,
            cpu_specification=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
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

        simulation_result, periodic_jobs, major_cycle = execute_simulation_major_cycle(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            cpu_specification=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
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
            execute_simulation_major_cycle(
                tasks=TaskSet(
                    periodic_tasks=periodic_tasks,
                    aperiodic_tasks=[],
                    sporadic_tasks=[]
                ),
                aperiodic_tasks_jobs=[],
                sporadic_tasks_jobs=[],
                cpu_specification=generate_default_cpu(number_of_cores, available_frequencies),
                environment_specification=default_environment_specification(),
                simulation_options=SimulationOptionsSpecification(id_debug=True),
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

        simulation_result, periodic_jobs, major_cycle = execute_simulation_major_cycle(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            cpu_specification=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
            scheduler=self.__simple_priority_scheduler_definition()
        )

        # Correct execution
        assert not simulation_result.have_been_scheduled
