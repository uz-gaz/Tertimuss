from tertimuss.cubed_space_thermal_simulator.materials_pack import FEAirForced
from .._environment_specification import EnvironmentSpecification


def default_environment_specification() -> EnvironmentSpecification:
    """
    Create a default environment
    :return: Environment specification
    """
    return EnvironmentSpecification(environment_properties=FEAirForced(), temperature=45 + 273.15)
