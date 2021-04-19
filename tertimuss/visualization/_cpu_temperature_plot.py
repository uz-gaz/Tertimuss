from typing import Optional

from matplotlib.animation import FuncAnimation

from tertimuss.cubed_space_thermal_simulator import generate_video_2d_heat_map, obtain_min_temperature, \
    generate_video_3d_heat_map, obtain_max_temperature
from tertimuss.simulation_lib.simulator import RawSimulationResult


def generate_board_temperature_evolution_2d_video(schedule_result: RawSimulationResult,
                                                  title: Optional[str] = None) -> FuncAnimation:
    """
    Generate a 2D animation of the evolution in the temperature of the processor

    :param schedule_result: Result of the simulation
    :param title: Plot title
    :return: plot
    """
    min_simulation_value = min(min(obtain_min_temperature(i).values())
                               for i in schedule_result.temperature_measures.values())
    max_simulation_value = max(max(obtain_max_temperature(i).values())
                               for i in schedule_result.temperature_measures.values())

    return generate_video_2d_heat_map(
        schedule_result.temperature_measures,
        min_temperature=min_simulation_value,
        max_temperature=max_simulation_value, axis="Z", location_in_axis=1, delay_between_frames_ms=100)


def generate_cpu_temperature_evolution_3d_video(schedule_result: RawSimulationResult,
                                                title: Optional[str] = None) -> FuncAnimation:
    """
    Generate a 2D animation of the evolution in the temperature of the processor

    :param schedule_result: Result of the simulation
    :param title: Plot title
    :return: plot
    """
    min_simulation_value = min(min(obtain_min_temperature(i).values())
                               for i in schedule_result.temperature_measures.values())
    max_simulation_value = max(max(obtain_max_temperature(i).values())
                               for i in schedule_result.temperature_measures.values())

    return generate_video_3d_heat_map(
        schedule_result.temperature_measures,
        min_temperature=min_simulation_value,
        max_temperature=max_simulation_value, delay_between_frames_ms=100)
