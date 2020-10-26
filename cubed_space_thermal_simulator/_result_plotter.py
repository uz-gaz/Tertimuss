import functools
from typing import List, Optional, Tuple, Literal

import numpy
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from cubed_space_thermal_simulator import TemperatureLocatedCube, obtain_min_temperature, obtain_max_temperature

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


def __obtain_rgb_heatmap_2_color_gradient(normalized_value: float) -> [float, float, float]:
    """
    Obtain color for heatmap
    Based on http://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients

    :param normalized_value: temperature value in the range [0, 1]
    :return: RGB representation
    """
    cold_r, cold_g, cold_b = [0.0, 0.0, 1.0]
    hot_r, hot_g, hot_b = [1.0, 0.0, 0.0]

    red = (hot_r - cold_r) * normalized_value + cold_r
    green = (hot_g - cold_g) * normalized_value + cold_g
    blue = (hot_b - cold_b) * normalized_value + cold_b
    return [red, green, blue]


def plot_3d_heat_map_temperature(heatmap_cube_list: List[TemperatureLocatedCube],
                                 min_temperature: Optional[float] = None,
                                 max_temperature: Optional[float] = None) -> Figure:
    # Obtain surrounded cube
    min_x = min([i.location.x for i in heatmap_cube_list])
    min_y = min([i.location.y for i in heatmap_cube_list])
    min_z = min([i.location.z for i in heatmap_cube_list])

    max_x = max([i.location.x + i.dimensions.x for i in heatmap_cube_list])
    max_y = max([i.location.y + i.dimensions.y for i in heatmap_cube_list])
    max_z = max([i.location.z + i.dimensions.z for i in heatmap_cube_list])

    # prepare some coordinates
    x, y, z = numpy.indices((max_x - min_x, max_y - min_y, max_z - min_z))

    # Colors array
    colors = numpy.zeros((max_x - min_x, max_y - min_y, max_z - min_z, 3))

    voxels_list = []

    # Min temperature

    min_temperature = obtain_min_temperature(heatmap_cube_list) if min_temperature is None else min_temperature
    max_temperature = obtain_max_temperature(heatmap_cube_list) if max_temperature is None else max_temperature

    for i in heatmap_cube_list:
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

                    # Obtain normalized temperature
                    normalized_temperature = (temperature - min_temperature) / (
                            max_temperature - min_temperature) if min_temperature != max_temperature else 0.5

                    # Obtain color
                    colors[local_x - min_x, local_y - min_y, local_z - min_z, 0], colors[
                        local_x - min_x, local_y - min_y, local_z - min_z, 1], colors[
                        local_x - min_x, local_y - min_y, local_z - min_z, 2] = __obtain_rgb_heatmap_2_color_gradient(
                        normalized_temperature)

    # combine the objects into a single boolean array
    voxels = functools.reduce(lambda a, b: a | b, voxels_list)

    # and plot everything
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.voxels(voxels, facecolors=colors)

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
    ax.set_axis_off()

    return fig


def generate_video_3d_heat_map(
        heatmap_cube_list: List[Tuple[float, List[TemperatureLocatedCube]]],
        min_temperature: Optional[float] = None,
        max_temperature: Optional[float] = None):
    pass


def plot_2d_heat_map(heatmap_cube_list: List[TemperatureLocatedCube],
                     axis: Literal["X", "Y", "Z"],
                     location_in_axis: int,
                     min_temperature: Optional[float] = None,
                     max_temperature: Optional[float] = None) -> Figure:
    # Obtain surrounded cube
    min_x = min([i.location.x for i in heatmap_cube_list])
    min_y = min([i.location.y for i in heatmap_cube_list])
    min_z = min([i.location.z for i in heatmap_cube_list])

    max_x = max([i.location.x + i.dimensions.x for i in heatmap_cube_list])
    max_y = max([i.location.y + i.dimensions.y for i in heatmap_cube_list])
    max_z = max([i.location.z + i.dimensions.z for i in heatmap_cube_list])

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

        for i in heatmap_cube_list:
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

        # Draw
        fig, ax = plt.subplots()

        max_range = max([plane_max_x - plane_min_x, plane_max_y - plane_min_y])

        # Calculate limits
        x_lim_min = plane_min_x - ((max_range - (plane_max_x - plane_min_x)) / 2)
        x_lim_max = plane_max_x + ((max_range - (plane_max_x - plane_min_x)) / 2)

        y_lim_min = plane_min_y - ((max_range - (plane_max_y - plane_min_y)) / 2)
        y_lim_max = plane_max_y + ((max_range - (plane_max_y - plane_min_y)) / 2)

        ax.set_xlim(x_lim_min, x_lim_max)
        ax.set_ylim(y_lim_min, y_lim_max)

        quad = ax.pcolormesh(heat_matrix, vmin=min_temperature, vmax=max_temperature, cmap="plasma")
        ax.set_xticks(numpy.arange(plane_min_x, plane_max_x + 1, 1.0))
        ax.set_yticks(numpy.arange(plane_min_y, plane_max_y + 1, 1.0))
        fig.colorbar(quad, ax=ax)
        return fig
