from typing import Optional

from matplotlib import pyplot
from matplotlib.figure import Figure

from tertimuss.simulation_lib.simulator import RawSimulationResult


def generate_memory_usage_plot(schedule_result: RawSimulationResult, title: Optional[str] = None) -> Figure:
    """
    Generate tasks execution plot
    :param schedule_result: Result of the simulation
    :param title: Plot title
    :return: plot
    """
    fig, ax = pyplot.subplots(nrows=1)
    time_vector, memory_usage_vector = zip(*[(i, j) for i, j in sorted(schedule_result.memory_usage_record.items(),
                                                                       key=lambda k: k[1])])

    # Set content
    ax[0].plot(time_vector, memory_usage_vector)
    ax[0].set_ylim(0, None)

    ax[0].set_ylabel(f'Memory usage (bytes)')
    ax[0].set_xlabel(f'Time (s)')

    # Set title
    if title is not None:
        fig.suptitle(title)

    # Adjust layout
    fig.tight_layout()

    return fig
