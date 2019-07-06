from typing import Optional

from core.kernel_generator.thermal_model_selector import ThermalModelSelector


class SimulationSpecification(object):
    """
    Specification of some parameters of the simulation
    """

    def __init__(self, step: Optional[float], dt: float):
        """

        :param step: Mesh step size (mm)
        :param dt:  Accuracy in seconds
        """
        self.step = step
        self.dt = dt

        # TODO: Put in the specification
        self.thermal_model_selector = ThermalModelSelector.THERMAL_MODEL_ENERGY_BASED
        self.dt_fragmentation = 10
