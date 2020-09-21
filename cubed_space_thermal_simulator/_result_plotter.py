import functools
from typing import List, Optional

import numpy
import matplotlib.pyplot as plt

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


def plot_3d_heat_map_temperature_located_cube_list(heatmap_cube_list: List[TemperatureLocatedCube],
                                                   min_temperature: Optional[float] = None,
                                                   max_temperature: Optional[float] = None):
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

    plt.show()
