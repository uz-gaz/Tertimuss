from typing import Optional

import scipy

from main.core.problem_specification.simulation_specification.SimulationPrecision import SimulationPrecision


class SimulationSpecification(object):
    """
    Specification of some parameters of the simulation
    """

    def __init__(self, step: Optional[float], dt: float, dt_fragmentation_processor_task: int = 16,
                 dt_fragmentation_thermal: int = 128, float_decimals_precision: int = 5,
                 type_precision: SimulationPrecision = SimulationPrecision.HIGH_PRECISION):
        """

        :param step: Mesh step size (mm)
        :param dt:  Accuracy in seconds
        """
        self.step: Optional[float] = step
        self.dt: float = dt
        self.dt_fragmentation_processor_task: int = dt_fragmentation_processor_task
        self.dt_fragmentation_thermal: int = dt_fragmentation_thermal
        self.float_decimals_precision: int = float_decimals_precision
        self.type_precision: scipy.dtype = type_precision.value[0]
