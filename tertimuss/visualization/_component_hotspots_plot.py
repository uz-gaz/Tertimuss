from typing import List, Optional, Literal

from matplotlib import pyplot
from matplotlib.figure import Figure

from tertimuss.cubed_space_thermal_simulator import obtain_max_temperature
from ..simulation_lib.simulator import RawSimulationResult


def generate_component_hotspots_plot(schedule_result: RawSimulationResult, start_time: float = 0,
                                     end_time: Optional[float] = None, title: Optional[str] = None,
                                     units: Literal["KELVIN", "CELSIUS"] = "KELVIN") -> Figure:
    """
    Generate a graphic with the temperature of the hotspots in the components (cores and board) over time

    :param units: Units where the temperature will be expressed
    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    cpu_ids: List[int] = sorted(schedule_result.job_sections_execution.keys())

    fig, ax = pyplot.subplots(nrows=len(cpu_ids) + 1)

    measures_times = list(sorted(schedule_result.temperature_measures.keys()))
    max_temperature_list = [obtain_max_temperature(schedule_result.temperature_measures[i]) for i in measures_times]

    # min_temperature = 0

    for cpu_id in cpu_ids + [len(cpu_ids)]:
        max_temperature_list_cpu_i = [i[cpu_id] - (0 if units == "KELVIN" else 273.15) for i in max_temperature_list]
        ax[cpu_id].plot(measures_times, max_temperature_list_cpu_i)

        ax[cpu_id].set_xlim(start_time, end_time)

        # Set label
        ax[cpu_id].set_xlabel(f'Time (s)')

        if cpu_id != len(cpu_ids):
            ax[cpu_id].set_ylabel(f'CPU {cpu_id} \n Temperature ({"K" if units == "KELVIN" else "ºC"})')
        else:
            ax[cpu_id].set_ylabel(f'Board \n Temperature ({"K" if units == "KELVIN" else "ºC"})')

    # Set uniform y_lim
    max_y = max(ax[i].get_ylim()[1] for i in range(len(cpu_ids) + 1))
    min_y = min(ax[i].get_ylim()[0] for i in range(len(cpu_ids) + 1))
    for i in range(len(cpu_ids) + 1):
        ax[i].set_ylim(min_y, max_y)

    # Set title
    if title is not None:
        fig.suptitle(title)

    # Adjust layout
    fig.tight_layout()

    return fig
