"""
This file pretends to define an example simulation result that can be used to test the plotting packages
"""
from typing import Optional, Tuple, List

from tertimuss.schedulers.g_edf import SGEDF
from tertimuss.simulation_lib.simulator import RawSimulationResult, \
    execute_scheduler_simulation, SimulationConfiguration
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, TaskSet, Job
from tertimuss.simulation_lib.system_definition.utils import default_environment_specification, generate_default_cpu


def create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
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


def get_simulation_result() -> Tuple[TaskSet, List[Job], RawSimulationResult]:
    periodic_tasks = [
        create_implicit_deadline_periodic_task_h_rt(3, 3000, 7.0, 3),
        create_implicit_deadline_periodic_task_h_rt(2, 4000, 7.0, 2),
        create_implicit_deadline_periodic_task_h_rt(1, 4000, 14.0, 1),
        create_implicit_deadline_periodic_task_h_rt(0, 3000, 14.0, 0)
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

    tasks = TaskSet(
        periodic_tasks=periodic_tasks,
        aperiodic_tasks=[],
        sporadic_tasks=[]
    )

    simulation_result = execute_scheduler_simulation(tasks=TaskSet(
        periodic_tasks=periodic_tasks,
        aperiodic_tasks=[],
        sporadic_tasks=[]
    ),
        jobs=jobs_list,
        processor_definition=generate_default_cpu(2, {1000}),
        environment_specification=default_environment_specification(),
        simulation_options=SimulationConfiguration(id_debug=True, thermal_simulation_type="DVFS",
                                                   simulate_thermal_behaviour=True),
        scheduler=SGEDF(True)
    )

    return tasks, jobs_list, simulation_result
