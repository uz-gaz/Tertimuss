import functools
from typing import List

import numpy
import matplotlib.pyplot as plt

from cubed_space_thermal_simulator import TemperatureLocatedCube


def plot_3d_heat_map_temperature_located_cube_list(heatmap_cube_list: List[TemperatureLocatedCube]):
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
    min_temperature = min([i.temperatureMatrix.min() for i in heatmap_cube_list])
    max_temperature = max([i.temperatureMatrix.max() for i in heatmap_cube_list])

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
                        (local_x - local_min_x) + (local_y - local_min_y) * i.dimensions.y + (
                                local_z - local_min_z) * i.dimensions.y * i.dimensions.x]

                    # TODO: Only print if min != max
                    colors[local_x - min_x, local_y - min_y, local_z - min_z, 0] = 0.5
                    colors[local_x - min_x, local_y - min_y, local_z - min_z, 1] = (temperature - min_temperature) / (
                                max_temperature - min_temperature)
                    colors[local_x - min_x, local_y - min_y, local_z - min_z, 2] = 0.5

    # combine the objects into a single boolean array
    voxels = functools.reduce(lambda a, b: a | b, voxels_list)
    # set the colors of each object
    # colors = numpy.empty(voxels.shape, dtype=object)
    # colors[:, :, :, 0] = 0.5
    # colors[:, :, :, 1] = 0.0
    # colors[:, :, :, 2] = 0.5
    # colors[cube1] = 'blue'
    # colors[cube2] = 'green'

    colors_mine = numpy.zeros((max_x - min_x, max_y - min_y, max_z - min_z, 3))

    # and plot everything
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.voxels(voxels, facecolors=colors)

    ax.set(xlabel='x', ylabel='y', zlabel='z')

    plt.show()
