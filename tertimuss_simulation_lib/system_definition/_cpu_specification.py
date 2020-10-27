import itertools
import math
from typing import List, Optional, Set


class EnergyConsumptionProperties(object):
    def __init__(self, leakage_alpha: float = 0.001, leakage_delta: float = 0.1, dynamic_alpha: float = 1.52,
                 dynamic_beta: float = 0.08):
        """
        Core construction properties relatives to the energy consumption

        Dynamic power = dynamic_alpha * F^3 + dynamic_beta

        Leakage power = current temperature * 2 * leakage_delta + leakage_alpha

        :param leakage_alpha: leakage_alpha
        :param leakage_delta: leakage_delta
        :param dynamic_alpha: dynamic_alpha
        :param dynamic_beta: dynamic_beta
        """
        # Leakage power properties
        self.leakage_delta: float = leakage_delta
        self.leakage_alpha: float = leakage_alpha

        # Dynamic power properties
        self.dynamic_alpha: float = dynamic_alpha
        self.dynamic_beta: float = dynamic_beta


class MaterialCuboid(object):

    def __init__(self, x: float, y: float, z: float, p: float, c_p: float, k: float):
        """
        Cuboid-shaped material object

        :param x: X size (mm)
        :param y: Y size (mm)
        :param z: Z size (mm)
        :param p: Density (Kg/cm^3)
        :param c_p: Specific heat capacities (J/Kg K)
        :param k: Thermal conductivity (W/m ºC)
        """
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.p: float = p
        self.c_p: float = c_p
        self.k: float = k


class BoardSpecification(object):
    def __init__(self, physical_properties: MaterialCuboid):
        """
        Specification of the board where the cores are located

        :param physical_properties: Board physical properties
        """
        self.physical_properties: MaterialCuboid = physical_properties


class Origin(object):

    def __init__(self, x: float, y: float):
        """
        Origins of material cuboid

        :param x: X coordinate (mm)
        :param y: Y coordinate (mm)
        """
        self.x: float = x
        self.y: float = y


class CoreGroupSpecification(object):
    def __init__(self, physical_properties: MaterialCuboid,
                 energy_consumption_properties: EnergyConsumptionProperties,
                 available_frequencies: Set[int],
                 cores_origins: Optional[List[Origin]] = None):
        """
        Specification of a group of cores with the same characteristics

        :param physical_properties: Cores physical properties
        :param energy_consumption_properties: Core construction properties relatives to the energy consumption
        :param available_frequencies: Cores available frequencies in H
        :param cores_origins: Cores origins locations
        """
        self.physical_properties: MaterialCuboid = physical_properties
        self.energy_consumption_properties: EnergyConsumptionProperties = energy_consumption_properties
        self.available_frequencies: Set[int] = available_frequencies
        self.cores_origins: Optional[List[Origin]] = cores_origins


class CpuSpecification(object):

    def __init__(self, board_specification: BoardSpecification, cores_specification: CoreGroupSpecification,
                 number_of_cores: int):
        """
        Specification of a processor

        :param board_specification: Specification of the board where cores are located
        :param cores_specification: Specification of the cores
        """
        self.board_specification: BoardSpecification = board_specification
        self.cores_specification: CoreGroupSpecification = cores_specification

        if self.cores_specification.cores_origins is None and board_specification is not None:
            # Generate automatic origins if none origins provided
            self.cores_specification.cores_origins = \
                self.__generate_automatic_origins(0, self.board_specification.physical_properties.x,
                                                  0, self.board_specification.physical_properties.y,
                                                  self.cores_specification.physical_properties.x,
                                                  self.cores_specification.physical_properties.y,
                                                  number_of_cores)

    @classmethod
    def __generate_automatic_origins(cls, x0: float, x1: float, y0: float, y1: float, mx: float, my: float,
                                     m: int) -> List[Origin]:
        """
        Generate automatic origins distributed over the board in a symmetrical way
        :param x0: board left edge position
        :param x1: board right edge position
        :param y0: board bottom edge position
        :param y1: board top edge position
        :param mx: core width
        :param my: core height
        :param m: number of cores
        :return:
        """
        if m == 1:
            return [Origin(x0 + (x1 - x0 - mx) / 2, y0 + (y1 - y0 - my) / 2)]
        else:
            if (x1 - x0) >= (y1 - y0):
                return cls.__generate_automatic_origins(x0, x0 + (x1 - x0) / 2, y0, y1, mx, my, math.ceil(m / 2)) + \
                       cls.__generate_automatic_origins(x0 + (x1 - x0) / 2, x1, y0, y1, mx, my, math.floor(m / 2))
            else:
                return cls.__generate_automatic_origins(x0, x1, y0, y0 + (y1 - y0) / 2, mx, my, math.ceil(m / 2)) + \
                       cls.__generate_automatic_origins(x0, x1, y0 + (y1 - y0) / 2, y1, mx, my, math.floor(m / 2))

    @staticmethod
    def check_origins(cpu_origins: List[Origin], x_size_cpu: float, y_size_cpu: float, x_size_board: float,
                      y_size_board: float) -> bool:
        """
        Checks if any core overlaps with other core

        :param x_size_board: width of the board
        :param y_size_cpu: height of the core
        :param x_size_cpu: width of the core
        :param y_size_board: height of the board
        :param cpu_origins: list of cpu cores origins
        :return: true if no core overlaps with other core and all have valid positions, false otherwise
        """

        def overlaps(cpu_1_origin: Origin, cpu_2_origin: Origin, x_size: float, y_size: float):
            """
            Check if two cores overlap

            :param cpu_1_origin: first core
            :param cpu_2_origin: second core
            :param x_size: width of the cores
            :param y_size: height of the cores
            :return: true if they overlap, false otherwise
            """
            return not ((cpu_1_origin.x > cpu_2_origin.x + x_size or cpu_2_origin.x > cpu_1_origin.x + x_size) or (
                    cpu_1_origin.y < cpu_2_origin.y + y_size or cpu_2_origin.y < cpu_1_origin.y))

        return all(
            [a.x + x_size_cpu <= x_size_board and a.y + y_size_cpu <= y_size_board for a in cpu_origins]) and not any(
            [overlaps(a[0], a[1], x_size_cpu, y_size_cpu) for a in itertools.combinations(cpu_origins, 2)])
