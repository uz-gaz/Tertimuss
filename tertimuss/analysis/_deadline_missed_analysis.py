from dataclasses import dataclass
from typing import Dict, Set, List

from ..simulation_lib.simulator import RawSimulationResult, JobSectionExecution
from ..simulation_lib.system_definition import TaskSet, Job, Task, PreemptiveExecution, Criticality


@dataclass(frozen=True)
class DeadlineMissedAnalysis:
    """
    Deadline missed analysis
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

    # Fully preemptive tasks
    number_of_missed_deadlines_fully_preemptive_tasks: int  # Total number of missed deadlines

    # Non preemptive tasks
    number_of_missed_deadlines_non_preemptive_tasks: int  # Total number of missed deadlines

    # Analysis by task
    number_of_missed_deadlines_by_task: Dict[int, int]  # Total number of missed deadlines by task id

    # Analysis by job
    has_missed_deadlines_by_job: Dict[int, bool]  # Total number of missed deadlines by job id

    # Lately cycles in missed soft real time tasks
    delay_in_soft_real_time_by_job: Dict[int, int]  # Cycles of delay after the deadline that the task took to finish


def __sum_items_by_condition(feature_count: Dict[int, int], allowed_actors: Set[int]) -> int:
    return sum(i for j, i in feature_count.items() if j in allowed_actors)


def obtain_deadline_misses_analysis(task_set: TaskSet, jobs: List[Job],
                                    schedule_result: RawSimulationResult) -> DeadlineMissedAnalysis:
    """
    Deadline missed analysis
    :param task_set: task set
    :param jobs: jobs of the task set
    :param schedule_result: simulation result
    :return: deadline missed analysis
    """
    tasks: List[Task] = task_set.periodic_tasks + task_set.aperiodic_tasks + task_set.sporadic_tasks

    # Analysis by job
    has_missed_deadlines_by_job: Dict[int, bool] = {i.identification: False for i in jobs}
    delay_in_soft_real_time_by_job: Dict[int, int] = {i.identification: 0 for i in jobs}

    # Analysis by task
    number_of_missed_deadlines_by_task: Dict[int, int] = {i.identification: 0 for i in tasks}

    for job in [i for i in jobs if i.task.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE]:
        job_execution: List[JobSectionExecution] = [i for cpu_number, job_sections_execution in
                                                    schedule_result.job_sections_execution.items() for
                                                    i in job_sections_execution if i.job_id == job.identification]

        job_execution = sorted(job_execution, key=lambda x: x.execution_start_time)

        job_executed_cycles = sum(i.number_of_executed_cycles for i in job_execution) \
            if job.task.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE \
            else (job_execution[-1].number_of_executed_cycles if len(job_execution) > 0 else 0)

        has_missed_deadlines_by_job[job.identification] = job.execution_time == job_executed_cycles
        delay_in_soft_real_time_by_job[job.identification] = job.execution_time - job_executed_cycles

        number_of_missed_deadlines_by_task[job.task.identification] = \
            number_of_missed_deadlines_by_task[job.task.identification] + \
            (0 if job.execution_time == job_executed_cycles else 1)

    periodic_tasks: Set[int] = {i.identification for i in task_set.periodic_tasks}
    aperiodic_tasks: Set[int] = {i.identification for i in task_set.aperiodic_tasks}
    sporadic_tasks: Set[int] = {i.identification for i in task_set.aperiodic_tasks}

    soft_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.SOFT}
    hard_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.HARD}
    firm_rt_tasks: Set[int] = {i.identification for i in tasks if i.deadline_criteria == Criticality.FIRM}

    fully_preemptive_tasks: Set[int] = {i.identification for i in tasks if
                                        i.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE}
    non_preemptive_tasks: Set[int] = {i.identification for i in tasks if
                                      i.preemptive_execution == PreemptiveExecution.NON_PREEMPTIVE}

    # All types of tasks
    number_of_missed_deadlines: int = sum(number_of_missed_deadlines_by_task.values())

    # Periodic tasks
    number_of_missed_deadlines_periodic_tasks: int = __sum_items_by_condition(number_of_missed_deadlines_by_task,
                                                                              periodic_tasks)

    # Aperiodic tasks
    number_of_missed_deadlines_aperiodic_tasks: int = __sum_items_by_condition(number_of_missed_deadlines_by_task,
                                                                               aperiodic_tasks)

    # Sporadic tasks
    number_of_missed_deadlines_sporadic_tasks: int = __sum_items_by_condition(number_of_missed_deadlines_by_task,
                                                                              sporadic_tasks)

    # Soft real time tasks
    number_of_missed_deadlines_soft_real_time_tasks: int = __sum_items_by_condition(number_of_missed_deadlines_by_task,
                                                                                    soft_rt_tasks)

    # Hard real time tasks
    number_of_missed_deadlines_hard_real_time_tasks: int = __sum_items_by_condition(number_of_missed_deadlines_by_task,
                                                                                    hard_rt_tasks)

    # Firm real time tasks
    number_of_missed_deadlines_firm_real_time_tasks: int = __sum_items_by_condition(number_of_missed_deadlines_by_task,
                                                                                    firm_rt_tasks)

    # Fully preemptive tasks
    number_of_missed_deadlines_fully_preemptive_tasks: int = __sum_items_by_condition(
        number_of_missed_deadlines_by_task,
        fully_preemptive_tasks)

    # Non preemptive tasks
    number_of_missed_deadlines_non_preemptive_tasks: int = __sum_items_by_condition(number_of_missed_deadlines_by_task,
                                                                                    non_preemptive_tasks)
    return DeadlineMissedAnalysis(
        has_missed_deadlines_by_job=has_missed_deadlines_by_job,
        delay_in_soft_real_time_by_job=delay_in_soft_real_time_by_job,
        number_of_missed_deadlines_by_task=number_of_missed_deadlines_by_task,
        number_of_missed_deadlines=number_of_missed_deadlines,
        number_of_missed_deadlines_periodic_tasks=number_of_missed_deadlines_periodic_tasks,
        number_of_missed_deadlines_aperiodic_tasks=number_of_missed_deadlines_aperiodic_tasks,
        number_of_missed_deadlines_sporadic_tasks=number_of_missed_deadlines_sporadic_tasks,
        number_of_missed_deadlines_soft_real_time_tasks=number_of_missed_deadlines_soft_real_time_tasks,
        number_of_missed_deadlines_hard_real_time_tasks=number_of_missed_deadlines_hard_real_time_tasks,
        number_of_missed_deadlines_firm_real_time_tasks=number_of_missed_deadlines_firm_real_time_tasks,
        number_of_missed_deadlines_fully_preemptive_tasks=number_of_missed_deadlines_fully_preemptive_tasks,
        number_of_missed_deadlines_non_preemptive_tasks=number_of_missed_deadlines_non_preemptive_tasks
    )
