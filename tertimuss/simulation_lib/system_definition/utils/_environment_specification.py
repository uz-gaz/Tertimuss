from tertimuss.cubed_space_thermal_simulator.materials_pack import AirForcedEnvironmentProperties
from .._environment_specification import EnvironmentSpecification


def default_environment_specification() -> EnvironmentSpecification:
    """
    Create a default environment
    :return: Environment specification
    """
    return EnvironmentSpecification(environment_properties=AirForcedEnvironmentProperties(), temperature=45 + 273.15)