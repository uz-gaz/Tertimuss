from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentSpecification(object):
    """
    Specification of the environment
    """
    # Convection factor (W/mm^2 ºC)
    h: float

    # Environment temperature (ºC)
    t: float
