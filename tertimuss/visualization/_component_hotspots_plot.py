from typing import List, Optional

from matplotlib import pyplot
from matplotlib.figure import Figure

from tertimuss.cubed_space_thermal_simulator import obtain_max_temperature
from ..simulation_lib.simulator import RawSimulationResult


def generate_component_hotspots_plot(schedule_result: RawSimulationResult, start_time: float = 0,
                                     end_time: Optional[float] = None, title: Optional[str] = None) -> Figure:
    cpu_ids: List[int] = sorted(schedule_result.job_sections_execution.keys())

    fig, ax = pyplot.subplots(nrows=len(cpu_ids) + 1)

    measures_times = list(sorted(schedule_result.temperature_measures.keys()))
    max_temperature_list = [obtain_max_temperature(schedule_result.temperature_measures[i]) for i in measures_times]

    min_temperature = 0

    for cpu_id in cpu_ids + [len(cpu_ids)]:
        max_temperature_list_cpu_i = [i[cpu_id] for i in max_temperature_list]
        ax[cpu_id].plot(measures_times, max_temperature_list_cpu_i)

        ax[cpu_id].set_xlim(start_time, end_time)

        # Set label
        ax[cpu_id].set_xlabel(f'Time (s)')

        if cpu_id != len(cpu_ids):
            ax[cpu_id].set_ylabel(f'CPU {cpu_id} \n Temperature (K)')
        else:
            ax[cpu_id].set_ylabel(f'Board \n Temperature (K)')

    # Set uniform y_lim
    max_y = max(ax[i].get_ylim()[1] for i in range(len(cpu_ids) + 1))
    for i in range(len(cpu_ids) + 1):
        ax[i].set_ylim(min_temperature, max_y)

    # Set title
    if title is not None:
        fig.suptitle(title)

    # Adjust layout
    fig.tight_layout()

    return fig
