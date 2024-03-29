import time
import unittest
from tertimuss.schedulers.run import SRUN
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationConfiguration
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, TaskSet
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification
from tests.schedulers._common_scheduler_tests_utils import create_implicit_deadline_periodic_task_h_rt, \
    periodic_implicit_deadline_tasks


class RUNTest(unittest.TestCase):
    def test_simple_simulation_periodic_task_set(self):
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0 + 1, 10000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(1 + 1, 5000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(2 + 1, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(3 + 1, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(4 + 1, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(5 + 1, 14000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(6 + 1, 3000, 5.0)
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
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=SRUN(activate_debug=True, store_clusters_obtained=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    def test_complex_simulation_periodic_task_set(self):
        task_set = TaskSet(
            periodic_tasks=[
                PeriodicTask(
                    identifier=0, worst_case_execution_time=63, relative_deadline=3.0,
                    best_case_execution_time=None, execution_time_distribution=None,
                    memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD, energy_consumption=None, phase=None,
                    period=3.0),
                PeriodicTask(
                    identifier=1, worst_case_execution_time=1976, relative_deadline=4.0,
                    best_case_execution_time=None,
                    execution_time_distribution=None, memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD,
                    energy_consumption=None, phase=None, period=4.0),
                PeriodicTask(
                    identifier=2, worst_case_execution_time=3408, relative_deadline=12.0,
                    best_case_execution_time=None,
                    execution_time_distribution=None, memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD,
                    energy_consumption=None, phase=None, period=12.0),
                PeriodicTask(
                    identifier=3, worst_case_execution_time=74, relative_deadline=2.0,
                    best_case_execution_time=None,
                    execution_time_distribution=None, memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD,
                    energy_consumption=None, phase=None, period=2.0),
                PeriodicTask(
                    identifier=4, worst_case_execution_time=3285, relative_deadline=15.0,
                    best_case_execution_time=None,
                    execution_time_distribution=None, memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD,
                    energy_consumption=None, phase=None, period=15.0),
                PeriodicTask(
                    identifier=5, worst_case_execution_time=2715, relative_deadline=5.0,
                    best_case_execution_time=None,
                    execution_time_distribution=None, memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD,
                    energy_consumption=None, phase=None, period=5.0),
                PeriodicTask(
                    identifier=6, worst_case_execution_time=408, relative_deadline=6.0,
                    best_case_execution_time=None,
                    execution_time_distribution=None, memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD,
                    energy_consumption=None, phase=None, period=6.0),
                PeriodicTask(
                    identifier=7, worst_case_execution_time=1336, relative_deadline=4.0,
                    best_case_execution_time=None,
                    execution_time_distribution=None, memory_footprint=None, priority=None,
                    preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                    deadline_criteria=Criticality.HARD,
                    energy_consumption=None, phase=None, period=4.0)], aperiodic_tasks=[],
            sporadic_tasks=[])

        number_of_cores = 2
        available_frequencies = {1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=SRUN(activate_debug=True, store_clusters_obtained=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        if simulation_result.hard_real_time_deadline_missed_stack_trace is not None:
            print(simulation_result.hard_real_time_deadline_missed_stack_trace.time)
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    def test_partitioned_task_set(self):
        task_set = TaskSet(periodic_tasks=[create_implicit_deadline_periodic_task_h_rt(j, i[0], i[1]) for j, i in
                                           enumerate(periodic_implicit_deadline_tasks)],
                           sporadic_tasks=[],
                           aperiodic_tasks=[])

        number_of_cores = 4
        available_frequencies = {1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=SRUN(activate_debug=True, store_clusters_obtained=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None
