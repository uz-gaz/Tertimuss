import os
import pickle
import time
import unittest
from tertimuss.schedulers.calecs import CALECSScheduler
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationOptionsSpecification
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, TaskSet
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification


class CALECSTest(unittest.TestCase):
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
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies, 0, 0),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
            scheduler=CALECSScheduler(activate_debug=True, store_clusters_obtained=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    def test_partitioned_task_set(self):
        with open(os.path.join(os.path.dirname(__file__), "_partitioned_task_set.pickle"), "rb") as text_file:
            task_set = pickle.load(text_file)

        number_of_cores = 4
        available_frequencies = {1000}

        start = time.time()

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies, 0, 0),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
            scheduler=CALECSScheduler(activate_debug=True, store_clusters_obtained=True)
        )

        end = time.time()

        print("Schedulers simulation time:", end - start)

        # with open("_partitioned_task_set_expected_solution_calecs.pickle", "wb") as text_file:
        #     pickle.dump((simulation_result, periodic_jobs, major_cycle), text_file)

        with open(os.path.join(os.path.dirname(__file__), "_partitioned_task_set_expected_solution_calecs.pickle"),
                  "rb") as text_file:
            (expected_simulation_result, expected_periodic_jobs, expected_major_cycle) = pickle.load(text_file)

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

        assert expected_simulation_result == simulation_result
        assert periodic_jobs == expected_periodic_jobs
        assert major_cycle == expected_major_cycle
