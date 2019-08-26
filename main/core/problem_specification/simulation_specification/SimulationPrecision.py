from enum import Enum

import scipy


class SimulationPrecision(Enum):
    """
    Simulation precision.

    Higher precision implies more resources consumption and more simulation time
    """
    HIGH_PRECISION = scipy.float64,
    MIDDLE_PRECISION = scipy.float32
