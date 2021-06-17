from dataclasses import dataclass

from tertimuss.cubed_space_thermal_simulator import FluidEnvironment


@dataclass(frozen=True)
class Environment:
    """
    Specification of the environment
    """
    environment_properties: FluidEnvironment
    """Environment properties"""

    temperature: float
    """Environment temperature (ºK)"""
