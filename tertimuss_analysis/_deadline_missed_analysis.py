from dataclasses import dataclass
from typing import Dict, Set, List

from tertimuss_simulation_lib.simulator import RawSimulationResult
from tertimuss_simulation_lib.system_definition import TaskSet, Job, Task, PreemptiveExecution, Criticality


@dataclass(frozen=True)
class DeadlineMissAnalysis:
    """
    Preemptions and migrations analysis of fully preemptive tasks
    """
    # All types of tasks
    number_of_missed_deadlines: int  # Total number of missed deadlines

    # Periodic tasks
    number_of_missed_deadlines_periodic_tasks: int  # Total number of missed deadlines

    # Aperiodic tasks
    number_of_missed_deadlines_aperiodic_tasks: int  # Total number of missed deadlines

    # Sporadic tasks
    number_of_missed_deadlines_sporadic_tasks: int  # Total number of missed deadlines

    # Soft real time tasks
    number_of_missed_deadlines_soft_real_time_tasks: int  # Total number of missed deadlines

    # Hard real time tasks
    number_of_missed_deadlines_hard_real_time_tasks: int  # Total number of missed deadlines

    # Firm real time tasks
    number_of_missed_deadlines_firm_real_time_tasks: int  # Total number of missed deadlines

    # Analysis by task
    number_of_missed_deadlines_by_task: Dict[int, int]  # Total number of missed deadlines by task id

    # Analysis by job
    number_of_missed_deadlines_by_job: Dict[int, int]  # Total number of missed deadlines by job id

    # TODO: Lately cycles in missed soft real time tasks
