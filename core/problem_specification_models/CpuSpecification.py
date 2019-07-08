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

    def __init__(self, board_specification: Optional[MaterialCuboid], cpu_core_specification: Optional[MaterialCuboid],
                 number_of_cores: int, clock_base_frequency: int, clock_frequencies_at_start: List[float],
                 clock_available_frequencies: List[float], cpu_origins: Optional[List[Origin]] = None):
        """
        CPU specification
        :param board_specification: Spec of board
        :param cpu_core_specification: Spec of homogeneous CPU core
        :param number_of_cores: Number of homogeneous CPU cores
        :param clock_base_frequency: Clock base frequency in Hz
        :param clock_frequencies_at_start: Frequency scale of homogeneous CPU cores relative to the base frequency
        :param clock_available_frequencies: Available frequencies scale of homogeneous CPU cores relative to the base
        frequency
        range: [0,1]
        """
        self.board_specification = board_specification
        self.cpu_core_specification = cpu_core_specification
        self.number_of_cores = number_of_cores
        self.clock_base_frequency = clock_base_frequency

        self.clock_available_frequencies = clock_available_frequencies
        self.clock_available_frequencies.sort()

        # TODO: This may be defined by the problem specification
        # Convection properties
        self.leakage_delta = 0.1
        self.leakage_alpha = 0.001

        # TODO: search an appropriate name for this variables
        # Heat generation properties
        self.dvfs_mult = 1.52
        self.dvfs_const = 0.08

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

        if cpu_origins is None and board_specification is not None:
            self.cpu_origins = generate_automatic_origins(0, self.board_specification.x, 0, self.board_specification.y,
                                                          self.cpu_core_specification.x, self.cpu_core_specification.y,
                                                          self.number_of_cores)
        else:
            self.cpu_origins = cpu_origins

        self.clock_relative_frequencies = clock_frequencies_at_start

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
