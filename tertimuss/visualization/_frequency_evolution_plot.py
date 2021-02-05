from typing import Optional, List
import itertools

from matplotlib import pyplot
from matplotlib.figure import Figure

from ..simulation_lib.simulator import RawSimulationResult


def generate_frequency_evolution_plot(schedule_result: RawSimulationResult, start_time: float = 0,
                                      end_time: Optional[float] = None, title: Optional[str] = None) -> Figure:
    """
    Generate tasks execution plot

    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    cpu_ids: List[int] = sorted(schedule_result.cpus_frequencies.keys())

    fig, ax = pyplot.subplots(nrows=len(cpu_ids), ncols=1)

    # Set content
    for i in range(len(cpu_ids)):
        time_vector, frequency_vector = zip(*itertools.chain(
            *[[(j.frequency_set_time, j.frequency_used), (j.frequency_unset_time, j.frequency_used)] for j in
              sorted(schedule_result.cpus_frequencies[i], key=lambda k: k.frequency_set_time)]))

        ax[i].plot(time_vector, frequency_vector)

        # Set limits
        ax[i].set_xlim(start_time, end_time)

    # Set uniform y_lim
    max_y = max(ax[i].get_ylim()[1] for i in range(len(cpu_ids)))
    for i in range(len(cpu_ids)):
        ax[i].set_ylim(0, max_y)

    # Set row and column titles
    for i, cpu_id in enumerate(cpu_ids):
        ax[i].set_ylabel(f'CPU {cpu_id}\nFrequency (Hz)')
        ax[i].set_xlabel(f'Time (s)')

    # Set title
    if title is not None:
        fig.suptitle(title)

    # Adjust layout
    fig.tight_layout()

    return fig
