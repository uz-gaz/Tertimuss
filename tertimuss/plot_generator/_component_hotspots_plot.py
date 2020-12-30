# TODO: This module will contain a function that over the time plot the max temperature in each core and in the board
# This module must uses only the functions provided by cubed_space_thermal_simulator (there must be a function that
# obtain the max temperature in a cuboid)
from matplotlib.figure import Figure

from tertimuss.simulation_lib.simulator import RawSimulationResult
from tertimuss.simulation_lib.system_definition import TaskSet, Optional


def generate_component_hotspots_plot(task_set: TaskSet, schedule_result: RawSimulationResult, start_time: float = 0,
                                     end_time: Optional[float] = None, title: Optional[str] = None) -> Figure:
    pass
