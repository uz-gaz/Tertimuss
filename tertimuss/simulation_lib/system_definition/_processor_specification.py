from dataclasses import dataclass
from typing import Set, Dict, Tuple

from tertimuss.cubed_space_thermal_simulator import UnitDimensions, SolidMaterial, UnitLocation


@dataclass(frozen=True)
class CoreEnergyConsumption:
    # TODO: This model should be revisited. Should find a model capable of model CMOS and FinFET circuits
    # Leakage power properties = current temperature * 2 * leakage_delta + leakage_alpha
    leakage_alpha: float  # Leakage alpha
    leakage_delta: float  # Leakage delta

    # Dynamic power properties = dynamic_alpha * F^3 + dynamic_beta
    dynamic_alpha: float  # Dynamic alpha
    dynamic_beta: float  # Dynamic beta


@dataclass(frozen=True)
class CoreTypeDefinition:
    dimensions: UnitDimensions  # Dimensions of the core type in units (the units are defined in the
    # #ProcessorDefinition class)
    material: SolidMaterial  # Material of the core type
    core_energy_consumption: CoreEnergyConsumption  # Core energy consumption properties
    available_frequencies: Set[int]  # Cores available frequencies in Hz
    preemption_cost: int  # Preemption cost in cycles


@dataclass(frozen=True)
class BoardDefinition:
    dimensions: UnitDimensions  # Dimensions of the board
    material: SolidMaterial  # Material of the board
    location: UnitLocation  # Location of the board


@dataclass(frozen=True)
class CoreDefinition:
    core_type: CoreTypeDefinition  # Core type of the core
    location: UnitLocation  # Location of the board


@dataclass(frozen=True)
class ProcessorDefinition:
    board_definition: BoardDefinition  # Definition of the CPU board
    cores_definition: Dict[int, CoreDefinition]  # Definition of each core. The key is the CPU id and the value the
    # definition
    migration_costs: Dict[Tuple[int, int], int]  # Cost of migrations in cycles. key = (core from, core to)
    measure_unit: float  # The measure unit in metres
