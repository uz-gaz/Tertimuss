from dataclasses import dataclass

from tertimuss.cubed_space_thermal_simulator import FluidEnvironmentProperties


@dataclass(frozen=True)
class EnvironmentSpecification:
    """
    Specification of the environment
    """
    environment_properties: FluidEnvironmentProperties
    """Environment properties"""

    temperature: float
    """Environment temperature (ºK)"""
