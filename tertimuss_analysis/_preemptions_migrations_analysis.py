from dataclasses import dataclass
from typing import Dict, List, Set

from tertimuss_simulation_lib.simulator import RawSimulationResult, PreemptiveExecution, Criticality
from tertimuss_simulation_lib.system_definition import TaskSet, Job, Task


@dataclass(frozen=True)
class PreemptionsMigrationsAnalysis:
    """
    Preemptions and migrations analysis of fully preemptive tasks
    """
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

    # Soft real time tasks
    number_of_migrations_soft_real_time_tasks: int  # Total number of migrations
    number_of_preemptions_soft_real_time_tasks: int  # Total number of preemptions

    # Hard real time tasks
    number_of_migrations_hard_real_time_tasks: int  # Total number of migrations
    number_of_preemptions_hard_real_time_tasks: int  # Total number of preemptions

    # Firm real time tasks
    number_of_migrations_firm_real_time_tasks: int  # Total number of migrations
    number_of_preemptions_firm_real_time_tasks: int  # Total number of preemptions

    # Analysis by task
    number_of_migrations_by_task: Dict[int, int]  # Total number of migrations by task id
    number_of_preemptions_by_task: Dict[int, int]  # Total number of preemptions by task id

    # Analysis by job
    number_of_migrations_by_job: Dict[int, int]  # Total number of migrations by job id
    number_of_preemptions_by_job: Dict[int, int]  # Total number of preemptions by job id


def __sum_items_by_condition(feature_count: Dict[int, int], allowed_actors: Set[int]) -> int:
    return sum(i for j, i in feature_count.items() if j in allowed_actors)


def obtain_preemptions_migrations_analysis(task_set: TaskSet, jobs: List[Job],
                                           schedule_result: RawSimulationResult) -> PreemptionsMigrationsAnalysis:
    """
    Preemptions and migrations analysis of fully preemptive tasks
    :param task_set:
    :param jobs:
    :param schedule_result:
    :return:
    """
    tasks: List[Task] = task_set.periodic_tasks + task_set.aperiodic_tasks + task_set.sporadic_tasks

    # Analysis by job
    number_of_migrations_by_job: Dict[int, int] = {i.identification: 0 for i in jobs if
                                                   i.task.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE}
    number_of_preemptions_by_job: Dict[int, int] = {i.identification: 0 for i in jobs if
                                                    i.task.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE}

    # Analysis by task
    number_of_migrations_by_task: Dict[int, int] = {i.identification: 0 for i in tasks if
                                                    i.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE}
    number_of_preemptions_by_task: Dict[int, int] = {i.identification: 0 for i in tasks if
                                                     i.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE}

    for job in [i for i in jobs if i.task.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE]:
        job_execution = [(cpu_number, i.execution_start_time) for cpu_number, job_sections_execution in
                         schedule_result.job_sections_execution.items() for i in job_sections_execution if
                         i.job_id == job.identification]

        job_execution = sorted(job_execution, key=lambda x: x[1])
        number_of_migrations = sum(1 for (i, j) in zip(job_execution, job_execution[1:]) if i[0] != j[0]) if len(
            job_execution) > 1 else 0
        number_of_preemptions = len(job_execution)

        number_of_migrations_by_job[job.identification] = number_of_migrations
        number_of_preemptions_by_job[job.identification] = number_of_preemptions

        number_of_migrations_by_task[job.task.identification] = number_of_migrations_by_task[
                                                                    job.task.identification] + number_of_migrations
        number_of_preemptions_by_task[job.task.identification] = number_of_preemptions_by_task[
                                                                     job.task.identification] + number_of_preemptions

    periodic_tasks: Set[int] = {i.identification for i in task_set.periodic_tasks}
    aperiodic_tasks: Set[int] = {i.identification for i in task_set.aperiodic_tasks}
    sporadic_tasks: Set[int] = {i.identification for i in task_set.aperiodic_tasks}

    soft_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.SOFT}
    hard_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.HARD}
    firm_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.FIRM}

    # All types of tasks
    number_of_migrations: int = sum(number_of_migrations_by_task.values())
    number_of_preemptions: int = sum(number_of_preemptions_by_task.values())

    # Periodic tasks
    number_of_migrations_periodic_tasks: int = __sum_items_by_condition(number_of_migrations_by_task, periodic_tasks)
    number_of_preemptions_periodic_tasks: int = __sum_items_by_condition(number_of_preemptions_by_task, periodic_tasks)

    # Aperiodic tasks
    number_of_migrations_aperiodic_tasks: int = __sum_items_by_condition(number_of_migrations_by_task, aperiodic_tasks)
    number_of_preemptions_aperiodic_tasks: int = __sum_items_by_condition(number_of_preemptions_by_task,
                                                                          aperiodic_tasks)

    # Sporadic tasks
    number_of_migrations_sporadic_tasks: int = __sum_items_by_condition(number_of_migrations_by_task, sporadic_tasks)
    number_of_preemptions_sporadic_tasks: int = __sum_items_by_condition(number_of_preemptions_by_task, sporadic_tasks)

    # Soft real time tasks
    number_of_migrations_soft_real_time_tasks: int = __sum_items_by_condition(number_of_migrations_by_task,
                                                                              soft_rt_tasks)
    number_of_preemptions_soft_real_time_tasks: int = __sum_items_by_condition(number_of_preemptions_by_task,
                                                                               soft_rt_tasks)

    # Hard real time tasks
    number_of_migrations_hard_real_time_tasks: int = __sum_items_by_condition(number_of_migrations_by_task,
                                                                              hard_rt_tasks)
    number_of_preemptions_hard_real_time_tasks: int = __sum_items_by_condition(number_of_preemptions_by_task,
                                                                               hard_rt_tasks)

    # Firm real time tasks
    number_of_migrations_firm_real_time_tasks: int = __sum_items_by_condition(number_of_migrations_by_task,
                                                                              firm_rt_tasks)
    number_of_preemptions_firm_real_time_tasks: int = __sum_items_by_condition(number_of_preemptions_by_task,
                                                                               firm_rt_tasks)

    return PreemptionsMigrationsAnalysis(number_of_migrations=number_of_migrations,
                                         number_of_preemptions=number_of_preemptions,
                                         number_of_migrations_periodic_tasks=number_of_migrations_periodic_tasks,
                                         number_of_preemptions_periodic_tasks=number_of_preemptions_periodic_tasks,
                                         number_of_migrations_aperiodic_tasks=number_of_migrations_aperiodic_tasks,
                                         number_of_preemptions_aperiodic_tasks=number_of_preemptions_aperiodic_tasks,
                                         number_of_migrations_sporadic_tasks=number_of_migrations_sporadic_tasks,
                                         number_of_preemptions_sporadic_tasks=number_of_preemptions_sporadic_tasks,
                                         number_of_migrations_soft_real_time_tasks
                                         =number_of_migrations_soft_real_time_tasks,
                                         number_of_preemptions_soft_real_time_tasks
                                         =number_of_preemptions_soft_real_time_tasks,
                                         number_of_migrations_hard_real_time_tasks
                                         =number_of_migrations_hard_real_time_tasks,
                                         number_of_preemptions_hard_real_time_tasks
                                         =number_of_preemptions_hard_real_time_tasks,
                                         number_of_migrations_firm_real_time_tasks
                                         =number_of_migrations_firm_real_time_tasks,
                                         number_of_preemptions_firm_real_time_tasks
                                         =number_of_preemptions_firm_real_time_tasks,
                                         number_of_migrations_by_job=number_of_migrations_by_job,
                                         number_of_preemptions_by_job=number_of_preemptions_by_job,
                                         number_of_migrations_by_task=number_of_migrations_by_task,
                                         number_of_preemptions_by_task=number_of_preemptions_by_task
                                         )
