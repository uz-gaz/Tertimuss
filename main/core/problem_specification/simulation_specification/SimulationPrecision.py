from enum import Enum

import numpy


class SimulationPrecision(Enum):
    """
    Simulation precision.

    Higher precision implies more resources consumption and more simulation time
    """
    HIGH_PRECISION = numpy.float64,
    MIDDLE_PRECISION = numpy.float32
