import time
import unittest
from tertimuss.schedulers.calecs import SCALECS
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationConfiguration
from tertimuss.simulation_lib.system_definition import TaskSet
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification
from tests.schedulers._common_scheduler_tests_utils import create_implicit_deadline_periodic_task_h_rt, \
    periodic_implicit_deadline_tasks


class CALECSTest(unittest.TestCase):
    def test_simple_simulation_periodic_task_set(self):
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 10000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(1, 5000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(2, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(3, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(4, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(5, 14000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(6, 3000, 5.0)
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
            scheduler=SCALECS(activate_debug=True, store_clusters_obtained=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
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
            scheduler=SCALECS(activate_debug=True, store_clusters_obtained=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None
