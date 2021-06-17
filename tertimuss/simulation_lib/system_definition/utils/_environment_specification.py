from tertimuss.cubed_space_thermal_simulator.materials_pack import FEAirForced
from .._environment_specification import Environment


def default_environment_specification() -> Environment:
    """
    Create a default environment
    :return: Environment specification
    """
    return Environment(environment_properties=FEAirForced(), temperature=45 + 273.15)
