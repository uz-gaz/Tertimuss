from dataclasses import dataclass
from typing import Dict, List

from tertimuss_simulation_lib.simulator import RawSimulationResult
from tertimuss_simulation_lib.system_definition import TaskSet, Job


@dataclass(frozen=True)
class PreemptionsMigrationsAnalysis:
    # All types of tasks
    number_of_migrations: int  # Total number of migrations
    number_of_preemptions: int  # Total number of preemptions (the number of scheduler produced preemptions is equal
    # to the total number of preemptions - number of jobs)

    # Periodic tasks
    number_of_migrations_periodic_tasks: int  # Total number of migrations
    number_of_preemptions_periodic_tasks: int  # Total number of preemptions

    # Aperiodic tasks
    number_of_migrations_aperiodic_tasks: int  # Total number of migrations
    number_of_preemptions_aperiodic_tasks: int  # Total number of preemptions

    # Sporadic tasks
    number_of_migrations_sporadic_tasks: int  # Total number of migrations
    number_of_preemptions_sporadic_tasks: int  # Total number of preemptions

    # Analysis by task
    number_of_migrations_by_task: Dict[int, int]  # Total number of migrations by task id
    number_of_preemptions_by_task: Dict[int, int]  # Total number of preemptions by task id

    # Analysis by job
    number_of_migrations_by_job: Dict[int, int]  # Total number of migrations by job id
    number_of_preemptions_by_job: Dict[int, int]  # Total number of preemptions by job id


def obtain_preemptions_migrations_analysis(tasks: TaskSet, jobs: List[Job],
                                           schedule_result: RawSimulationResult) -> PreemptionsMigrationsAnalysis:
    pass
