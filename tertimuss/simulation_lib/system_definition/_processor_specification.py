from dataclasses import dataclass
from typing import Set, Dict

from tertimuss.cubed_space_thermal_simulator import UnitDimensions, SolidMaterial, UnitLocation


@dataclass(frozen=True)
class CoreEnergyConsumption:
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
class CoreTypeDefinition:
    """
    Specification of a type of core
    """
    dimensions: UnitDimensions
    """Dimensions of the core type in units (the units are defined in the ProcessorDefinition class)"""

    material: SolidMaterial
    """Material of the core type"""

    core_energy_consumption: CoreEnergyConsumption
    """Core energy consumption properties"""

    available_frequencies: Set[int]
    """Cores available frequencies in Hz"""

    # preemption_cost: int  # Preemption cost in cycles


@dataclass(frozen=True)
class BoardDefinition:
    """
    Specification of the board where cores are placed
    """
    dimensions: UnitDimensions
    """Dimensions of the board"""

    material: SolidMaterial
    """Material of the board"""

    location: UnitLocation
    """Location of the board"""


@dataclass(frozen=True)
class CoreDefinition:
    """
    Specification of a core in the system
    """
    core_type: CoreTypeDefinition
    """Core type of the core"""

    location: UnitLocation
    """Location of the board"""


@dataclass(frozen=True)
class ProcessorDefinition:
    """
    Specification of the processor
    """
    board_definition: BoardDefinition
    """Definition of the CPU board"""

    cores_definition: Dict[int, CoreDefinition]
    """Definition of each core. The key is the CPU id and the value the definition"""

    # migration_costs: Dict[Tuple[int, int], int]  # Cost of migrations in cycles. key = (core from, core to)

    measure_unit: float
    """The measure unit in metres"""
