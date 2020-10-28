import itertools
import math
from dataclasses import dataclass
from typing import List, Set


@dataclass(frozen=True)
class EnergyConsumptionProperties:
    # Leakage power properties = current temperature * 2 * leakage_delta + leakage_alpha
    leakage_alpha: float  # Leakage alpha
    leakage_delta: float  # Leakage delta

    # Dynamic power properties = dynamic_alpha * F^3 + dynamic_beta
    dynamic_alpha: float  # Dynamic alpha
    dynamic_beta: float  # Dynamic beta


@dataclass(frozen=True)
class MaterialCuboid:
    # Cuboid-shaped material object
    x: float  # X size (mm)
    y: float  # Y size (mm)
    z: float  # Z size (mm)
    p: float  # Density (Kg/cm^3)
    c_p: float  # Specific heat capacities (J/Kg K)
    k: float  # Thermal conductivity (W/m ºC)


@dataclass(frozen=True)
class BoardSpecification:
    # Specification of the board where the cores are located
    physical_properties: MaterialCuboid  # Board physical properties


@dataclass(frozen=True)
class Origin:
    # Origins of material cuboid
    x: float  # X coordinate (mm)
    y: float  # Y coordinate (mm)


@dataclass(frozen=True)
class CoreGroupSpecification:
    #  Specification of a group of cores with the same characteristics
    physical_properties: MaterialCuboid  # Cores physical properties
    energy_consumption_properties: EnergyConsumptionProperties  # Core energy consumption properties
    available_frequencies: Set[int]  # Cores available frequencies in Hz
    cores_origins: List[Origin]  # Cores origins locations


@dataclass(frozen=True)
class CpuSpecification:
    # Specification of a processor
    board_specification: BoardSpecification  # Specification of the board where cores are located
    cores_specification: CoreGroupSpecification  # Specification of the cores


def generate_automatic_core_origins(x0: float, x1: float, y0: float, y1: float, mx: float, my: float,
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
            return generate_automatic_core_origins(x0, x0 + (x1 - x0) / 2, y0, y1, mx, my, math.ceil(m / 2)) + \
                   generate_automatic_core_origins(x0 + (x1 - x0) / 2, x1, y0, y1, mx, my, math.floor(m / 2))
        else:
            return generate_automatic_core_origins(x0, x1, y0, y0 + (y1 - y0) / 2, mx, my, math.ceil(m / 2)) + \
                   generate_automatic_core_origins(x0, x1, y0 + (y1 - y0) / 2, y1, mx, my, math.floor(m / 2))


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
