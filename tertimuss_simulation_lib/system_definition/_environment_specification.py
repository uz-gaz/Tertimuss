from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentSpecification(object):
    """
    Specification of the environment
    """
    # Convection factor (W/mm^2 ºC)
    convection_factor: float

    # Environment temperature (ºC)
    temperature: float
