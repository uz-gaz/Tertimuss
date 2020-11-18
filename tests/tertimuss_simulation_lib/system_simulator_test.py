import unittest
from typing import Set, Dict, Optional, Tuple, Union, List

from tertimuss_simulation_lib.simulator import execute_simulation_major_cycle, TaskSet, SimulationOptionsSpecification, \
    CentralizedAbstractScheduler
from tertimuss_simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, \
    HomogeneousCpuSpecification, EnvironmentSpecification
from tertimuss_simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification


class SystemSimulatorTest(unittest.TestCase):

    @staticmethod
    def __simple_scheduler_definition() -> CentralizedAbstractScheduler:
        class SimpleEDFCentralized(CentralizedAbstractScheduler):
            def __init__(self):
                super().__init__(True)
                self.__active_jobs: Set[int] = set()
                self.__m = 0

            def check_schedulability(self, cpu_specification: Union[HomogeneousCpuSpecification],
                                     environment_specification: EnvironmentSpecification, task_set: TaskSet) \
                    -> [bool, Optional[str]]:
                return True, None

            def offline_stage(self, cpu_specification: Union[HomogeneousCpuSpecification],
                              environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
                self.__m = cpu_specification.cores_specification.number_of_cores
                return max(cpu_specification.cores_specification.available_frequencies)

            def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                                jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                                cores_max_temperature: Optional[Dict[int, float]]) -> Tuple[
                Dict[int, int], Optional[int], Optional[int]]:
                tasks_to_execute = sorted(self.__active_jobs)
                return {j: i for i, j in zip(tasks_to_execute, range(self.__m))}, None, None

            def on_major_cycle_start(self, global_time: float) -> bool:
                return True

            def on_jobs_activation(self, global_time: float, activation_time: float,
                                   jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
                self.__active_jobs = Set.union(self.__active_jobs, {i for i, j in jobs_id_tasks_ids})
                return True

            def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
                self.__active_jobs = Set.difference(self.__active_jobs, {i for i in jobs_id})
                return True

            def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
                self.__active_jobs = Set.difference(self.__active_jobs, {i for i in jobs_id})
                return True

        return SimpleEDFCentralized()

    @staticmethod
    def __create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                      period: float) -> PeriodicTask:
        return PeriodicTask(task_id, worst_case_execution_time, period, None, None, None, None,
                            PreemptiveExecution.FULLY_PREEMPTIVE, Criticality.FIRM, None, None, period)

    def test_simple_simulation_periodic_task_set(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(0, 3000, 7),
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 7),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 14),
            self.__create_implicit_deadline_periodic_task_h_rt(3, 3000, 14)
        ]

        number_of_cores = 2
        available_frequencies = {1000}

        simulation_result = execute_simulation_major_cycle(TaskSet(
            periodic_tasks=periodic_tasks,
            aperiodic_tasks=[],
            sporadic_tasks=[]
        ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            cpu_specification=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
            scheduler=self.__simple_scheduler_definition()
        )

        # Expected execution
        #
        # 0   3    7  10   14
        # +-----------------+
        # |T0 |T2  |T0 |    |
        # +-----------------+
        #
        # 0    4   7   11  14
        # +-----------------+
        # |T1  |T3 |T1  |   |
        # +-----------------+


        i = 0
