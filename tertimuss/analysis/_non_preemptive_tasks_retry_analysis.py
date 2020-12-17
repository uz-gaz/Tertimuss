from dataclasses import dataclass
from typing import Dict, Set, List

from ..simulation_lib.simulator import RawSimulationResult
from ..simulation_lib.system_definition import TaskSet, Job, Task, PreemptiveExecution, Criticality


@dataclass(frozen=True)
class NonPreemptiveTasksRetryAnalysis:
    """
    Retries analysis of non preemptive tasks
    """
    # All types of tasks
    number_of_retries: int  # Total number of retries

    # Periodic tasks
    number_of_retries_periodic_tasks: int  # Total number of retries

    # Aperiodic tasks
    number_of_retries_aperiodic_tasks: int  # Total number of retries

    # Sporadic tasks
    number_of_retries_sporadic_tasks: int  # Total number of retries

    # Soft real time tasks
    number_of_retries_soft_real_time_tasks: int  # Total number of retries

    # Hard real time tasks
    number_of_retries_hard_real_time_tasks: int  # Total number of retries

    # Firm real time tasks
    number_of_retries_firm_real_time_tasks: int  # Total number of retries

    # Analysis by task
    number_of_retries_by_task: Dict[int, int]  # Total number of retries by task id
    number_of_used_cycles_by_task: Dict[int, int]  # Total number of cycles used by task id (counting the cycles used in
    # the retries)

    # Analysis by job
    number_of_retries_by_job: Dict[int, int]  # Total number of retries by job id
    number_of_used_cycles_by_job: Dict[int, int]  # Total number of cycles used by task id (counting the cycles used in
    # the retries)


def __sum_items_by_condition(feature_count: Dict[int, int], allowed_actors: Set[int]) -> int:
    return sum(i for j, i in feature_count.items() if j in allowed_actors)


def obtain_non_preemptive_tasks_retries_analysis(task_set: TaskSet, jobs: List[Job],
                                                 schedule_result: RawSimulationResult) \
        -> NonPreemptiveTasksRetryAnalysis:
    """
    Retries analysis of non preemptive tasks
    :param task_set:
    :param jobs:
    :param schedule_result:
    :return:
    """
    tasks: List[Task] = task_set.periodic_tasks + task_set.aperiodic_tasks + task_set.sporadic_tasks

    # Analysis by task
    number_of_retries_by_task: Dict[int, int] = {i.identification: 0 for i in tasks if
                                                 i.preemptive_execution == PreemptiveExecution.NON_PREEMPTIVE}
    number_of_used_cycles_by_task: Dict[int, int] = {i.identification: 0 for i in tasks if
                                                     i.preemptive_execution == PreemptiveExecution.NON_PREEMPTIVE}

    # Analysis by job
    number_of_retries_by_job: Dict[int, int] = {i.identification: 0 for i in jobs if
                                                i.task.preemptive_execution == PreemptiveExecution.NON_PREEMPTIVE}
    number_of_used_cycles_by_job: Dict[int, int] = {i.identification: 0 for i in jobs if
                                                    i.task.preemptive_execution == PreemptiveExecution.NON_PREEMPTIVE}

    for job in [i for i in jobs if i.task.preemptive_execution == PreemptiveExecution.NON_PREEMPTIVE]:
        number_of_tries = sum(sum(1 for j in i if j.job_id == job.identification) for i in
                              schedule_result.job_sections_execution.values())
        number_of_used_cycles = sum(
            sum(j.number_of_executed_cycles for j in i if j.job_id == job.identification) for i in
            schedule_result.job_sections_execution.values())

        number_of_retries = number_of_tries - 1 if number_of_tries > 0 else 0

        number_of_retries_by_job[job.identification] = number_of_retries

        number_of_retries_by_task[job.task.identification] = number_of_retries_by_task[
                                                                 job.task.identification] + number_of_retries

        number_of_used_cycles_by_job[job.identification] = number_of_used_cycles

        number_of_used_cycles_by_task[job.task.identification] = number_of_used_cycles_by_task[
                                                                     job.task.identification] + number_of_retries

    periodic_tasks: Set[int] = {i.identification for i in task_set.periodic_tasks}
    aperiodic_tasks: Set[int] = {i.identification for i in task_set.aperiodic_tasks}
    sporadic_tasks: Set[int] = {i.identification for i in task_set.aperiodic_tasks}

    soft_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.SOFT}
    hard_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.HARD}
    firm_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.FIRM}

    # All types of tasks
    number_of_retries: int = sum(number_of_used_cycles_by_task.values())

    # Periodic tasks
    number_of_retries_periodic_tasks: int = __sum_items_by_condition(number_of_retries_by_task, periodic_tasks)

    # Aperiodic tasks
    number_of_retries_aperiodic_tasks: int = __sum_items_by_condition(number_of_retries_by_task, aperiodic_tasks)

    # Sporadic tasks
    number_of_retries_sporadic_tasks: int = __sum_items_by_condition(number_of_retries_by_task, sporadic_tasks)

    # Soft real time tasks
    number_of_retries_soft_real_time_tasks: int = __sum_items_by_condition(number_of_retries_by_task, soft_rt_tasks)

    # Hard real time tasks
    number_of_retries_hard_real_time_tasks: int = __sum_items_by_condition(number_of_retries_by_task, hard_rt_tasks)

    # Firm real time tasks
    number_of_retries_firm_real_time_tasks: int = __sum_items_by_condition(number_of_retries_by_task, firm_rt_tasks)

    return NonPreemptiveTasksRetryAnalysis(
        number_of_retries=number_of_retries,
        number_of_retries_periodic_tasks=number_of_retries_periodic_tasks,
        number_of_retries_aperiodic_tasks=number_of_retries_aperiodic_tasks,
        number_of_retries_sporadic_tasks=number_of_retries_sporadic_tasks,
        number_of_retries_soft_real_time_tasks=number_of_retries_soft_real_time_tasks,
        number_of_retries_hard_real_time_tasks=number_of_retries_hard_real_time_tasks,
        number_of_retries_firm_real_time_tasks=number_of_retries_firm_real_time_tasks,
        number_of_retries_by_task=number_of_retries_by_task,
        number_of_used_cycles_by_task=number_of_used_cycles_by_task,
        number_of_retries_by_job=number_of_retries_by_job,
        number_of_used_cycles_by_job=number_of_used_cycles_by_job
    )
