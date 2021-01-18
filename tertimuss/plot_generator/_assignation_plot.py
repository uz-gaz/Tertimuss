from typing import Dict, Optional, List

from matplotlib import pyplot, patches
from matplotlib.figure import Figure

from ._color_palette_generator import AbstractColorPaletteGenerator, DefaultColorPaletteGenerator
from ..simulation_lib.simulator import RawSimulationResult, calculate_major_cycle
from ..simulation_lib.system_definition import TaskSet, Job


def generate_task_assignation_plot(
        task_set: TaskSet, schedule_result: RawSimulationResult, start_time: float = 0,
        end_time: Optional[float] = None, title: Optional[str] = None,
        outline_boxes: bool = False,
        color_palette_generator: AbstractColorPaletteGenerator = DefaultColorPaletteGenerator()) -> Figure:
    """
    Generate tasks to CPUs assignation plot
    :param color_palette_generator: color palette applied to the plot
    :param outline_boxes: If true will outline the boxes
    :param task_set: Task set
    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    num_colors = len(task_set.tasks())

    tasks_color_id: Dict[int, int] = {j.identification: i for i, j in enumerate(task_set.tasks())}

    color_palette = color_palette_generator.obtain_color_palette(num_colors)

    fig, ax = pyplot.subplots()

    for cpu_id, sections_list in schedule_result.job_sections_execution.items():
        for section in sections_list:
            ax.barh(cpu_id, width=section.execution_end_time - section.execution_start_time,
                    left=section.execution_start_time, color=color_palette[tasks_color_id[section.task_id]],
                    edgecolor='black' if outline_boxes else None)

    ax.set_yticks(range(len(schedule_result.job_sections_execution)))
    ax.set_yticklabels([f'CPU {i}' for i in schedule_result.job_sections_execution.keys()])

    tasks_legend = [patches.Patch(color=color_palette[j], label=f'Task {i}') for i, j in
                    sorted(tasks_color_id.items(), key=lambda k: k[0])]

    ax.legend(handles=tasks_legend, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    end_time = end_time if end_time is not None else calculate_major_cycle(task_set)

    ax.set_xlim(start_time, end_time)

    # Set label
    ax.set_xlabel(f'Time (s)')

    # Set title
    if title is not None:
        ax.set_title(title)

    # Adjust layout
    fig.tight_layout()

    return fig


def generate_job_assignation_plot(
        task_set: TaskSet, jobs: List[Job], schedule_result: RawSimulationResult,
        start_time: float = 0, end_time: Optional[float] = None,
        title: Optional[str] = None, outline_boxes: bool = False,
        color_palette_generator: AbstractColorPaletteGenerator = DefaultColorPaletteGenerator()) -> Figure:
    """
    Generate jobs to CPUs assignation plot
    :param color_palette_generator: color palette applied to the plot
    :param outline_boxes: If true will outline the boxes
    :param task_set: Task set
    :param jobs: Jobs in the system
    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    num_colors = len(jobs)

    jobs_color_id: Dict[int, int] = {j.identification: i for i, j in enumerate(jobs)}

    color_palette = color_palette_generator.obtain_color_palette(num_colors)

    fig, ax = pyplot.subplots()

    for cpu_id, sections_list in schedule_result.job_sections_execution.items():
        for section in sections_list:
            ax.barh(cpu_id, width=section.execution_end_time - section.execution_start_time,
                    left=section.execution_start_time, color=color_palette[jobs_color_id[section.job_id]],
                    edgecolor='black' if outline_boxes else None)

    ax.set_yticks(range(len(schedule_result.job_sections_execution)))
    ax.set_yticklabels([f'CPU {i}' for i in schedule_result.job_sections_execution.keys()])

    jobs_legend = [patches.Patch(color=color_palette[j], label=f'Job {i}') for i, j in
                   sorted(jobs_color_id.items(), key=lambda k: k[0])]

    ax.legend(handles=jobs_legend, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    end_time = end_time if end_time is not None else calculate_major_cycle(task_set)

    ax.set_xlim(start_time, end_time)

    # Set label
    ax.set_xlabel(f'Time (s)')

    # Set title
    if title is not None:
        ax.set_title(title)

    # Adjust layout
    fig.tight_layout()

    return fig
