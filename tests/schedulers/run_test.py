import unittest
from tertimuss.schedulers.run import RUNScheduler
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationOptionsSpecification
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, TaskSet
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification


class RUNTest(unittest.TestCase):
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
            self.__create_implicit_deadline_periodic_task_h_rt(0 + 1, 10000, 20.0),
            self.__create_implicit_deadline_periodic_task_h_rt(1 + 1, 5000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(2 + 1, 7000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(3 + 1, 7000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(4 + 1, 7000, 10.0),
            self.__create_implicit_deadline_periodic_task_h_rt(5 + 1, 14000, 20.0),
            self.__create_implicit_deadline_periodic_task_h_rt(6 + 1, 3000, 5.0)
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
            scheduler=RUNScheduler()
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None
