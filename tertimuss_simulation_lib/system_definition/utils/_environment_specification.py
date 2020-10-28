from tertimuss_simulation_lib.system_definition import EnvironmentSpecification


def default_environment_specification() -> EnvironmentSpecification:
    """
    Create a default environment
    :return: Environment specification
    """
    return EnvironmentSpecification(h=0.001, t=45)
