from dataclasses import dataclass
from typing import Set, Dict

from tertimuss.cubed_space_thermal_simulator import Dimensions, SolidMaterial, Location


@dataclass(frozen=True)
class EnergyConsumption:
    """Specification of the energy consumption
     Leakage power consumption = current temperature * 2 * leakage_delta + leakage_alpha
     Dynamic power consumption = dynamic_alpha * F^3 + dynamic_beta
     Total energy consumption = Leakage power consumption + Dynamic power consumption
     """
    leakage_alpha: float
    """Leakage alpha"""

    leakage_delta: float
    """Leakage delta"""

    dynamic_alpha: float
    """Dynamic alpha"""

    dynamic_beta: float
    """Dynamic beta"""


@dataclass(frozen=True)
class CoreModel:
    """
    Specification of a type of core
    """
    dimensions: Dimensions
    """Dimensions of the core type in units (the units are defined in the ProcessorDefinition class)"""

    material: SolidMaterial
    """Material of the core type"""

    core_energy_consumption: EnergyConsumption
    """Core energy consumption properties"""

    available_frequencies: Set[int]
    """Cores available frequencies in Hz"""


@dataclass(frozen=True)
class Board:
    """
    Specification of the board where cores are placed
    """
    dimensions: Dimensions
    """Dimensions of the board"""

    material: SolidMaterial
    """Material of the board"""

    location: Location
    """Location of the board"""


@dataclass(frozen=True)
class Core:
    """
    Specification of a core in the system
    """
    core_type: CoreModel
    """Core type of the core"""

    location: Location
    """Location of the board"""


@dataclass(frozen=True)
class Processor:
    """
    Specification of the processor
    """
    board_definition: Board
    """Definition of the CPU board"""

    cores_definition: Dict[int, Core]
    """Definition of each core. The key is the CPU id and the value the definition"""

    measure_unit: float
    """The measure unit in metres"""
