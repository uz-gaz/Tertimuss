from enum import Enum

import scipy


class SimulationPrecision(Enum):
    """
    Select the simulation precision.

    Higher precision implies more resources consumption and long simulation time
    """
    HIGH_PRECISION = scipy.float64,
    MIDDLE_PRECISION = scipy.float32
