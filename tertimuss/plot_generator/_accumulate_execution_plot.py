from typing import Optional, List

from matplotlib import pyplot
from matplotlib.figure import Figure

from ..simulation_lib.simulator import RawSimulationResult, calculate_major_cycle
from ..simulation_lib.system_definition import TaskSet, Job


def generate_accumulate_execution_plot(task_set: TaskSet, schedule_result: RawSimulationResult, start_time: float = 0,
                                       end_time: Optional[float] = None, title: Optional[str] = None) -> Figure:
    """
    Generate tasks accumulative execution plot
    :param task_set: Task set
    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    tasks_ids: List[int] = sorted([i.identification for i in task_set.periodic_tasks + task_set.aperiodic_tasks +
                                   task_set.sporadic_tasks])
    cpu_ids: List[int] = sorted(schedule_result.job_sections_execution.keys())

    fig, ax = pyplot.subplots(nrows=len(cpu_ids), ncols=len(tasks_ids))

    end_time = end_time if end_time is not None else calculate_major_cycle(task_set)

    tasks_cc = {i.identification: i.worst_case_execution_time for i in task_set.periodic_tasks +
                task_set.aperiodic_tasks + task_set.sporadic_tasks}

    # Set content
    for i in range(len(cpu_ids)):
        for j in range(len(tasks_ids)):
            task_execution = [i for i in schedule_result.job_sections_execution[i] if i.task_id == j]
            task_execution = sorted(task_execution, key=lambda k: k.execution_start_time)
            accumulated_times: List[float] = [0]
            accumulated_cycles: List[int] = [0]
            total_accumulated_cycles = 0
            for r in task_execution:
                accumulated_cycles.append(total_accumulated_cycles)
                accumulated_times.append(r.execution_start_time)
                total_accumulated_cycles += r.number_of_executed_cycles
                accumulated_cycles.append(total_accumulated_cycles)
                accumulated_times.append(r.execution_end_time)

            if accumulated_times[-1] < end_time:
                accumulated_times.append(end_time)
                accumulated_cycles.append(total_accumulated_cycles)

            ax[i, j].plot(accumulated_times, accumulated_cycles)

            # Set limits
            ax[i, j].set_xlim(start_time, end_time)
            ax[i, j].set_ylim(0, tasks_cc[j])

    # Set row and column titles
    for i, task_id in enumerate(tasks_ids):
        for j, cpu_id in enumerate(cpu_ids):
            if j == len(cpu_ids) - 1:
                ax[j, i].set_xlabel(f'Time (s)\nTask {task_id}')
            else:
                ax[j, i].set_xlabel(f'Time (s)')

            if i == 0:
                ax[j, i].set_ylabel(f'CPU {cpu_id}\nExecution (cycles)')
            else:
                ax[j, i].set_ylabel(f'Execution (cycles)')

    # Set title
    if title is not None:
        fig.suptitle(title)

    # Adjust layout
    fig.tight_layout()

    return fig


def generate_job_accumulate_execution_plot(task_set: TaskSet, jobs: List[Job], schedule_result: RawSimulationResult,
                                           start_time: float = 0, end_time: Optional[float] = None,
                                           title: Optional[str] = None) -> Figure:
    """
    Generate jobs accumulative execution plot
    :param task_set: Task set
    :param jobs: Jobs in the system
    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    jobs_ids: List[int] = sorted([i.identification for i in jobs])

    cpu_ids: List[int] = sorted(schedule_result.job_sections_execution.keys())

    fig, ax = pyplot.subplots(nrows=len(cpu_ids), ncols=len(jobs_ids))

    end_time = end_time if end_time is not None else calculate_major_cycle(task_set)

    jobs_cc = {i.identification: i.execution_time for i in jobs}

    # Set content
    for i in range(len(cpu_ids)):
        for j in range(len(jobs_ids)):
            task_execution = [i for i in schedule_result.job_sections_execution[i] if i.job_id == j]
            task_execution = sorted(task_execution, key=lambda k: k.execution_start_time)
            accumulated_times: List[float] = [0]
            accumulated_cycles: List[int] = [0]
            total_accumulated_cycles = 0
            for r in task_execution:
                accumulated_cycles.append(total_accumulated_cycles)
                accumulated_times.append(r.execution_start_time)
                total_accumulated_cycles += r.number_of_executed_cycles
                accumulated_cycles.append(total_accumulated_cycles)
                accumulated_times.append(r.execution_end_time)

            if accumulated_times[-1] < end_time:
                accumulated_times.append(end_time)
                accumulated_cycles.append(total_accumulated_cycles)

            ax[i, j].plot(accumulated_times, accumulated_cycles)

            # Set limits
            ax[i, j].set_xlim(start_time, end_time)
            ax[i, j].set_ylim(0, jobs_cc[j])

    # Set row and column titles
    for i, job_id in enumerate(jobs_cc):
        for j, cpu_id in enumerate(cpu_ids):
            if j == len(cpu_ids) - 1:
                ax[j, i].set_xlabel(f'Job (s)\nTask {job_id}')
            else:
                ax[j, i].set_xlabel(f'Time (s)')

            if i == 0:
                ax[j, i].set_ylabel(f'CPU {cpu_id}\nExecution (cycles)')
            else:
                ax[j, i].set_ylabel(f'Execution (cycles)')

    # Set title
    if title is not None:
        fig.suptitle(title)

    # Adjust layout
    fig.tight_layout()

    return fig
