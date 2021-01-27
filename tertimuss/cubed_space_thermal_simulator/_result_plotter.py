import functools
from typing import Optional, Tuple, Literal, Dict

import numpy
import matplotlib.pyplot as plt
from matplotlib import cm, colors, animation
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

from tertimuss.cubed_space_thermal_simulator._basic_types import TemperatureLocatedCube, ThermalUnits
from tertimuss.cubed_space_thermal_simulator._cubed_space import obtain_min_temperature, obtain_max_temperature


def __obtain_3d_heat_map(heatmap_cube_list: Dict[int, TemperatureLocatedCube],
                         min_temperature: Optional[float],
                         max_temperature: Optional[float],
                         color_map: str):
    """
    Obtain 3d heat map of the model

    :param heatmap_cube_list: List with model temperature
    :param min_temperature: Min temperature in the model
    :param max_temperature: Max temperature in the model
    :return: Resultant figure representation
    """
    # Obtain surrounded cube
    min_x = min([i.location.x for i in heatmap_cube_list.values()])
    min_y = min([i.location.y for i in heatmap_cube_list.values()])
    min_z = min([i.location.z for i in heatmap_cube_list.values()])

    max_x = max([i.location.x + i.dimensions.x for i in heatmap_cube_list.values()])
    max_y = max([i.location.y + i.dimensions.y for i in heatmap_cube_list.values()])
    max_z = max([i.location.z + i.dimensions.z for i in heatmap_cube_list.values()])

    # prepare some coordinates
    x, y, z = numpy.indices((max_x - min_x, max_y - min_y, max_z - min_z))

    # Colors array
    voxels_colors = numpy.zeros((max_x - min_x, max_y - min_y, max_z - min_z, 3))

    voxels_list = []

    # Color transformer
    color_mappable = cm.ScalarMappable(norm=colors.Normalize(min_temperature, max_temperature), cmap=color_map)

    for i in heatmap_cube_list.values():
        local_min_x = i.location.x
        local_min_y = i.location.y
        local_min_z = i.location.z

        local_max_x = i.location.x + i.dimensions.x
        local_max_y = i.location.y + i.dimensions.y
        local_max_z = i.location.z + i.dimensions.z

        cube = (local_min_x <= x) & (local_min_y <= y) & (local_min_z <= z) & (x < local_max_x) & (y < local_max_y) & (
                z < local_max_z)
        voxels_list.append(cube)

        for local_x in range(local_min_x, local_max_x):
            for local_y in range(local_min_y, local_max_y):
                for local_z in range(local_min_z, local_max_z):
                    temperature = i.temperatureMatrix[
                        (local_x - local_min_x) + (local_y - local_min_y) * i.dimensions.x + (
                                local_z - local_min_z) * i.dimensions.y * i.dimensions.x]

                    # Obtain color
                    rgb_color = color_mappable.to_rgba(temperature)
                    voxels_colors[local_x - min_x, local_y - min_y, local_z - min_z, 0], voxels_colors[
                        local_x - min_x, local_y - min_y, local_z - min_z, 1], voxels_colors[
                        local_x - min_x, local_y - min_y, local_z - min_z, 2] = rgb_color[0], rgb_color[1], rgb_color[2]

    # combine the objects into a single boolean array
    voxels = functools.reduce(lambda a, b: a | b, voxels_list)

    return voxels, voxels_colors, min_x, max_x, min_y, max_y, min_z, max_z


def plot_3d_heat_map_temperature(heatmap_cube_list: Dict[int, TemperatureLocatedCube],
                                 min_temperature: Optional[float] = None,
                                 max_temperature: Optional[float] = None,
                                 color_map: str = "plasma",
                                 units: ThermalUnits = ThermalUnits.KELVIN) -> Figure:
    """
    Plot 3d heat map of the model

    :param heatmap_cube_list: List with model temperature
    :param min_temperature: Min temperature in the model
    :param max_temperature: Max temperature in the model
    :param color_map: Model color map
    :param units: Thermal units
    :return: Resultant figure
    """
    # Min temperature
    min_temperature = obtain_min_temperature(heatmap_cube_list) if min_temperature is None else min_temperature
    max_temperature = obtain_max_temperature(heatmap_cube_list) if max_temperature is None else max_temperature

    # Obtain representation
    voxels, voxels_colors, min_x, max_x, min_y, max_y, min_z, max_z = __obtain_3d_heat_map(heatmap_cube_list,
                                                                                           min_temperature,
                                                                                           max_temperature,
                                                                                           color_map)

    # Plot everything
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set(xlabel='x', ylabel='y', zlabel='z')

    ax.voxels(voxels, facecolors=voxels_colors)

    max_range = max([max_x - min_x, max_y - min_y, max_z - min_z])

    # Calculate limits
    x_lim_min = min_x - ((max_range - (max_x - min_x)) / 2)
    x_lim_max = max_x + ((max_range - (max_x - min_x)) / 2)

    y_lim_min = min_y - ((max_range - (max_y - min_y)) / 2)
    y_lim_max = max_y + ((max_range - (max_y - min_y)) / 2)

    z_lim_min = min_z - ((max_range - (max_z - min_z)) / 2)
    z_lim_max = max_z + ((max_range - (max_z - min_z)) / 2)

    ax.set_xlim(x_lim_min, x_lim_max)
    ax.set_ylim(y_lim_min, y_lim_max)
    ax.set_zlim(z_lim_min, z_lim_max)

    # Hide grid lines
    ax.grid(b=None)

    cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(min_temperature, max_temperature), cmap=color_map),
                        ax=ax)
    cbar.ax.set_ylabel("Temperature in " + ("kelvin" if units == ThermalUnits.KELVIN else "celsius"))
    return fig


def generate_video_3d_heat_map(
        heatmap_cube_list_dict: Dict[float, Dict[int, TemperatureLocatedCube]],
        delay_between_frames_ms: int,
        min_temperature: Optional[float] = None,
        max_temperature: Optional[float] = None,
        color_map: str = "plasma",
        units: ThermalUnits = ThermalUnits.KELVIN) -> FuncAnimation:
    """
    Generate a 3D video of heat map

    :param delay_between_frames_ms: Delay between two frames in milliseconds
    :param heatmap_cube_list_dict: Dict with parameters [time in seconds, list with model temperature]
    :param min_temperature: Min temperature in the model
    :param max_temperature: Max temperature in the model
    :param color_map: Model color map
    :param units: Thermal units
    :return: Resultant figure animation
    """
    min_x = min(
        [min([i.location.x for i in heatmap_cube_list.values()]) for heatmap_cube_list in
         heatmap_cube_list_dict.values()])
    min_y = min(
        [min([i.location.y for i in heatmap_cube_list.values()]) for heatmap_cube_list in
         heatmap_cube_list_dict.values()])
    min_z = min(
        [min([i.location.z for i in heatmap_cube_list.values()]) for heatmap_cube_list in
         heatmap_cube_list_dict.values()])

    max_x = max(
        [max([i.location.x + i.dimensions.x for i in heatmap_cube_list.values()]) for heatmap_cube_list in
         heatmap_cube_list_dict.values()])
    max_y = max(
        [max([i.location.y + i.dimensions.y for i in heatmap_cube_list.values()]) for heatmap_cube_list in
         heatmap_cube_list_dict.values()])
    max_z = max(
        [max([i.location.z + i.dimensions.z for i in heatmap_cube_list.values()]) for heatmap_cube_list in
         heatmap_cube_list_dict.values()])

    min_temperature = min([obtain_min_temperature(heatmap_cube_list) for heatmap_cube_list in
                           heatmap_cube_list_dict.values()]) if min_temperature is None else min_temperature
    max_temperature = max([obtain_max_temperature(heatmap_cube_list) for heatmap_cube_list in
                           heatmap_cube_list_dict.values()]) if max_temperature is None else max_temperature

    sorted_times = sorted(heatmap_cube_list_dict.keys())

    elapsed_time = sorted_times[-1] - sorted_times[0]

    # This is used to show the last frame some time
    last_frame_time = sorted_times[-1] - sorted_times[-2]

    number_of_frames = round((elapsed_time + last_frame_time) * 1000 / delay_between_frames_ms)

    frames_to_dict_mapper = {
        i: next(x for x, y in zip(sorted_times, sorted_times[1:] + [sorted_times[-1] + last_frame_time + 1]) if
                x <= (i * delay_between_frames_ms) / 1000 < y) for
        i in range(number_of_frames)}

    # Plot everything
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set(xlabel='x', ylabel='y', zlabel='z')

    max_range = max([max_x - min_x, max_y - min_y, max_z - min_z])

    # Calculate limits
    x_lim_min = min_x - ((max_range - (max_x - min_x)) / 2)
    x_lim_max = max_x + ((max_range - (max_x - min_x)) / 2)

    y_lim_min = min_y - ((max_range - (max_y - min_y)) / 2)
    y_lim_max = max_y + ((max_range - (max_y - min_y)) / 2)

    z_lim_min = min_z - ((max_range - (max_z - min_z)) / 2)
    z_lim_max = max_z + ((max_range - (max_z - min_z)) / 2)

    ax.set_xlim(x_lim_min, x_lim_max)
    ax.set_ylim(y_lim_min, y_lim_max)
    ax.set_zlim(z_lim_min, z_lim_max)

    # Hide grid lines
    ax.grid(b=None)

    cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(min_temperature, max_temperature), cmap=color_map),
                        ax=ax)
    cbar.ax.set_ylabel("Temperature in " + ("kelvin" if units == ThermalUnits.KELVIN else "celsius"))

    def animate(i):
        heatmap_cube_list_local, heatmap_cube_list_local_time = heatmap_cube_list_dict[frames_to_dict_mapper[i]], \
                                                                frames_to_dict_mapper[i]
        # Draw title
        fig.suptitle("Simulation time: " + str(heatmap_cube_list_local_time) + " seconds", fontsize=12)

        # Obtain representation
        voxels, voxels_colors, _, _, _, _, _, _ = __obtain_3d_heat_map(heatmap_cube_list_local,
                                                                       min_temperature,
                                                                       max_temperature,
                                                                       color_map)

        return ax.voxels(voxels, facecolors=voxels_colors)

    return animation.FuncAnimation(fig, animate, frames=number_of_frames, interval=delay_between_frames_ms, blit=False,
                                   repeat=False)


def __obtain_2d_heat_matrix(heatmap_cube_list: Dict[int, TemperatureLocatedCube],
                            axis: Literal["X", "Y", "Z"],
                            location_in_axis: int) -> Optional[Tuple[numpy.ndarray, float, float, float, float]]:
    """
    Obtain 2d heat map of the model

    :param location_in_axis: Location in the axis
    :param axis: Axis to plot
    :param heatmap_cube_list: List with model temperature
    :return: Resultant figure representation
    """
    # Obtain surrounded cube
    min_x = min([i.location.x for i in heatmap_cube_list.values()])
    min_y = min([i.location.y for i in heatmap_cube_list.values()])
    min_z = min([i.location.z for i in heatmap_cube_list.values()])

    max_x = max([i.location.x + i.dimensions.x for i in heatmap_cube_list.values()])
    max_y = max([i.location.y + i.dimensions.y for i in heatmap_cube_list.values()])
    max_z = max([i.location.z + i.dimensions.z for i in heatmap_cube_list.values()])

    is_location_correct: bool = (axis == "X" and min_x <= location_in_axis <= max_x) or (
            axis == "Y" and min_y <= location_in_axis <= max_y) or (
                                        axis == "Z" and min_z <= location_in_axis <= max_z)

    if is_location_correct:
        # Obtain plane sizes
        plane_min_x, plane_max_x = (min_x, max_x) if axis == "Y" else (
            (min_x, max_x) if axis == "Z" else (min_y, max_y))

        plane_min_y, plane_max_y = (min_z, max_z) if axis == "Y" else (
            (min_y, max_y) if axis == "Z" else (min_z, max_z))

        # Array where the heat matrix will be stored
        heat_matrix: numpy.ndarray = numpy.full((plane_max_y - plane_min_y, plane_max_x - plane_min_x), numpy.NaN)
        mask = numpy.ones((plane_max_y - plane_min_y, plane_max_x - plane_min_x))

        for i in heatmap_cube_list.values():
            local_min_x = i.location.x
            local_min_y = i.location.y
            local_min_z = i.location.z

            local_max_x = i.location.x + i.dimensions.x
            local_max_y = i.location.y + i.dimensions.y
            local_max_z = i.location.z + i.dimensions.z

            representation_x_offset = i.location.x - min_x
            representation_y_offset = i.location.y - min_y
            representation_z_offset = i.location.z - min_z

            if axis == "X" and local_min_x <= location_in_axis < local_max_x:
                local_x = location_in_axis - i.location.x
                for local_z in range(0, i.dimensions.z):
                    for local_y in range(0, i.dimensions.y):
                        temperature_value = i.temperatureMatrix[
                            local_x + local_y * i.dimensions.x + local_z * i.dimensions.y * i.dimensions.x]

                        heat_matrix[
                            representation_z_offset + local_z, representation_y_offset + local_y] = temperature_value

                        mask[representation_z_offset + local_z, representation_y_offset + local_y] = False

            elif axis == "Y" and local_min_y <= location_in_axis < local_max_y:
                local_y = location_in_axis - i.location.y
                for local_z in range(0, i.dimensions.z):
                    for local_x in range(0, i.dimensions.x):
                        temperature_value = i.temperatureMatrix[
                            local_x + local_y * i.dimensions.x + local_z * i.dimensions.y * i.dimensions.x]

                        heat_matrix[
                            representation_z_offset + local_z, representation_x_offset + local_x] = temperature_value

                        mask[representation_z_offset + local_z, representation_x_offset + local_x] = False

            elif axis == "Z" and local_min_z <= location_in_axis < local_max_z:
                local_z = location_in_axis - i.location.z
                for local_y in range(0, i.dimensions.y):
                    for local_x in range(0, i.dimensions.x):
                        temperature_value = i.temperatureMatrix[
                            local_x + local_y * i.dimensions.x + local_z * i.dimensions.y * i.dimensions.x]

                        heat_matrix[
                            representation_y_offset + local_y, representation_x_offset + local_x] = temperature_value

        return heat_matrix, plane_min_x, plane_max_x, plane_min_y, plane_max_y

    else:
        return None


def plot_2d_heat_map(heatmap_cube_list: Dict[int, TemperatureLocatedCube],
                     axis: Literal["X", "Y", "Z"],
                     location_in_axis: int,
                     min_temperature: Optional[float] = None,
                     max_temperature: Optional[float] = None,
                     color_map: str = "plasma",
                     units: ThermalUnits = ThermalUnits.KELVIN) -> Optional[Figure]:
    """
    Plot 2d heat map of the model

    :param location_in_axis: Location in the axis
    :param axis: Axis to plot
    :param heatmap_cube_list: List with model temperature
    :param min_temperature: Min temperature in the model
    :param max_temperature: Max temperature in the model
    :param color_map: Model color map
    :param units: Thermal units
    :return: Resultant figure
    """

    # Obtain heat matrix
    heat_matrix_result = __obtain_2d_heat_matrix(heatmap_cube_list, axis, location_in_axis)
    if heat_matrix_result is not None:
        heat_matrix, plane_min_x, plane_max_x, plane_min_y, plane_max_y = heat_matrix_result

        # Range
        max_range = max([plane_max_x - plane_min_x, plane_max_y - plane_min_y])

        # Calculate limits
        x_lim_min = plane_min_x - ((max_range - (plane_max_x - plane_min_x)) / 2)
        x_lim_max = plane_max_x + ((max_range - (plane_max_x - plane_min_x)) / 2)

        y_lim_min = plane_min_y - ((max_range - (plane_max_y - plane_min_y)) / 2)
        y_lim_max = plane_max_y + ((max_range - (plane_max_y - plane_min_y)) / 2)

        # Draw
        fig, ax = plt.subplots()

        ax.set_xlim(x_lim_min, x_lim_max)
        ax.set_ylim(y_lim_min, y_lim_max)

        quad = ax.pcolormesh(heat_matrix, vmin=min_temperature, vmax=max_temperature, cmap=color_map)
        ax.set_xticks(numpy.arange(plane_min_x, plane_max_x + 1, 1.0))
        ax.set_yticks(numpy.arange(plane_min_y, plane_max_y + 1, 1.0))
        cbar = fig.colorbar(quad, ax=ax)
        cbar.ax.set_ylabel("Temperature in " + ("kelvin" if units == ThermalUnits.KELVIN else "celsius"))
        return fig
    else:
        return None


def generate_video_2d_heat_map(
        heatmap_cube_list_dict: Dict[float, Dict[int, TemperatureLocatedCube]],
        axis: Literal["X", "Y", "Z"],
        location_in_axis: int,
        delay_between_frames_ms: int,
        min_temperature: Optional[float] = None,
        max_temperature: Optional[float] = None,
        color_map: str = "plasma",
        units: ThermalUnits = ThermalUnits.KELVIN) -> FuncAnimation:
    """
    Plot 2d heat map of the model

    :param delay_between_frames_ms: Delay between two frames in milliseconds
    :param location_in_axis: Location in the axis
    :param axis: Axis to plot
    :param heatmap_cube_list_dict: Dict with parameters [time in seconds, list with model temperature]
    :param min_temperature: Min temperature in the model
    :param max_temperature: Max temperature in the model
    :param color_map: Model color map
    :param units: Thermal units
    :return: Resultant figure animation
    """

    sorted_times = sorted(heatmap_cube_list_dict.keys())

    elapsed_time = sorted_times[-1] - sorted_times[0]

    # This is used to show the last frame some time
    last_frame_time = sorted_times[-1] - sorted_times[-2]

    number_of_frames = round((elapsed_time + last_frame_time) * 1000 / delay_between_frames_ms)

    frames_to_dict_mapper = {
        i: next(x for x, y in zip(sorted_times, sorted_times[1:] + [sorted_times[-1] + last_frame_time + 1]) if
                x <= (i * delay_between_frames_ms) / 1000 < y) for
        i in range(number_of_frames)}

    fig, ax = plt.subplots()
    cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(min_temperature, max_temperature), cmap=color_map),
                        ax=ax)
    cbar.ax.set_ylabel("Temperature in " + ("kelvin" if units == ThermalUnits.KELVIN else "celsius"))

    def animate(i):
        heatmap_cube_list_local, heatmap_cube_list_local_time = heatmap_cube_list_dict[frames_to_dict_mapper[i]], \
                                                                frames_to_dict_mapper[i]

        # Draw title
        fig.suptitle("Simulation time: " + str(heatmap_cube_list_local_time) + " seconds", fontsize=12)

        # Obtain heat matrix
        heat_matrix_result = __obtain_2d_heat_matrix(heatmap_cube_list_local, axis, location_in_axis)

        heat_matrix, plane_min_x, plane_max_x, plane_min_y, plane_max_y = heat_matrix_result

        # Range
        max_range = max([plane_max_x - plane_min_x, plane_max_y - plane_min_y])

        # Calculate limits
        x_lim_min = plane_min_x - ((max_range - (plane_max_x - plane_min_x)) / 2)
        x_lim_max = plane_max_x + ((max_range - (plane_max_x - plane_min_x)) / 2)

        y_lim_min = plane_min_y - ((max_range - (plane_max_y - plane_min_y)) / 2)
        y_lim_max = plane_max_y + ((max_range - (plane_max_y - plane_min_y)) / 2)

        ax.set_xlim(x_lim_min, x_lim_max)
        ax.set_ylim(y_lim_min, y_lim_max)
        ax.set_xticks(numpy.arange(plane_min_x, plane_max_x + 1, 1.0))
        ax.set_yticks(numpy.arange(plane_min_y, plane_max_y + 1, 1.0))

        quad = ax.pcolormesh(heat_matrix, vmin=min_temperature, vmax=max_temperature, cmap=color_map)

        return quad

    return animation.FuncAnimation(fig, animate, frames=number_of_frames, interval=delay_between_frames_ms, blit=False,
                                   repeat=False)
