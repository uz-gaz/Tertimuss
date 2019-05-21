import itertools
import math
from typing import Optional, List


class MaterialCuboid(object):
    """
    Material object with cuboid' shape
    """

    def __init__(self, x: float, y: float, z: float, p: float, c_p: float, k: float):
        """

        :param x: X coordinate size (mm)
        :param y: Y coordinate size (mm)
        :param z: Z coordinate size (mm)
        :param p: Density (Kg/cm^3)
        :param c_p: Specific heat capacities (J/Kg K)
        :param k: Thermal conductivity (W/m ºC)
        """
        self.x = x
        self.y = y
        self.z = z
        self.p = p
        self.c_p = c_p
        self.k = k


class Origin(object):
    """
    Origins of material cuboid
    """

    def __init__(self, x: float, y: float):
        """

        :param x: X coordinate (mm)
        :param y: Y coordinate (mm)
        """
        self.x = x
        self.y = y


class CoreSpecification(object):
    """
    Spec of a core
    """

    def __init__(self, cpu_core: MaterialCuboid, clock_frequency: float, origin: Origin):
        """

        :param cpu_core: Spec of core
        :param clock_frequency: Frequency
        :param origin: Origin position of core
        """
        self.cpu_core = cpu_core
        self.clock_frequency = clock_frequency
        self.origin = origin


class CpuSpecification(object):

    def __init__(self, board: Optional[MaterialCuboid], cpu_core: Optional[MaterialCuboid], number_of_cores: int,
                 clock_frequency: float, cpu_origins: Optional[List[Origin]] = None):
        """
        CPU specification
        :param board: Spec of board
        :param cpu_core: Spec of homogeneous CPU core
        :param number_of_cores: Number of homogeneous CPU cores
        :param clock_frequency: Frequency scale of homogeneous CPU cores (1 is the base frequency at which the platform could operate)
        """
        self.board = board
        self.cpu_core = cpu_core
        self.number_of_cores = number_of_cores
        self.clock_frequencies = number_of_cores * [clock_frequency]

        def generate_automatic_origins(x0: float, x1: float, y0: float, y1: float, mx: float, my: float,
                                       n: int) -> List[Origin]:
            # Distribute CPUs in a symmetrical way
            if n == 1:
                return [Origin(x0 + (x1 - x0 - mx) / 2, y0 + (y1 - y0 - my) / 2)]
            else:
                if (x1 - x0) >= (y1 - y0):
                    return generate_automatic_origins(x0, x0 + (x1 - x0) / 2, y0, y1, mx, my, math.ceil(n / 2)) + \
                           generate_automatic_origins(x0 + (x1 - x0) / 2, x1, y0, y1, mx, my, math.floor(n / 2))
                else:
                    return generate_automatic_origins(x0, x1, y0, y0 + (y1 - y0) / 2, mx, my, math.ceil(n / 2)) + \
                           generate_automatic_origins(x0, x1, y0 + (y1 - y0) / 2, y1, mx, my, math.floor(n / 2))

        if cpu_origins is None and board is not None:
            self.cpu_origins = generate_automatic_origins(0, self.board.x, 0, self.board.y, self.cpu_core.x,
                                                          self.cpu_core.y, self.number_of_cores)
        else:
            self.cpu_origins = cpu_origins

    '''
        # Constructor for heterogeneous CPU cores  
        def __init__(self, board: MaterialCuboid, cpu_cores: list):
            self.board = board  # Spec of board
            self.cpu_cores = cpu_cores  # Spec of heterogeneous CPU cores

    '''


def check_origins(cpu_origins: List[Origin], x_size_cpu: float, y_size_cpu: float, x_size_board: float,
                  y_size_board: float) -> bool:
    """
    Return true if no core overlap
    :param x_size_board: x size of board
    :param y_size_cpu: y size of core
    :param x_size_cpu: x size of core
    :param y_size_board: y size of board
    :param cpu_origins: cpu core origins list
    :return: true if no core overlap with others and all are valid
    """

    def overlaps(cpu_1_origin: Origin, cpu_2_origin: Origin, x_size: float, y_size: float):
        """
        Return true if cpu 1 and cpu 2 overlaps
        Ref: https://www.geeksforgeeks.org/find-two-rectangles-overlap/

        :param cpu_1_origin: cpu 1 origins
        :param cpu_2_origin: cpu 2 origins
        :param x_size: cpus x size
        :param y_size: cpus y size
        :return: true if overlaps false otherwise
        """
        return not ((cpu_1_origin.x > cpu_2_origin.x + x_size or cpu_2_origin.x > cpu_1_origin.x + x_size) or (
                cpu_1_origin.y < cpu_2_origin.y + y_size or cpu_2_origin.y < cpu_1_origin.y))

    return all(
        map(lambda a: a.x + x_size_cpu <= x_size_board and a.y + y_size_cpu <= y_size_board, cpu_origins)) and not any(
        map(lambda a: overlaps(a[0], a[1], x_size_cpu, y_size_cpu), itertools.combinations(cpu_origins, 2)))
