from typing import Optional


class SimulationSpecification(object):
    """
    Specification of some parameters of the simulation
    """

    def __init__(self, step: Optional[float], dt: float):
        """

        :param step: Mesh step size (mm)
        :param dt:  Accuracy (s)
        """
        self.step = step
        self.dt = dt
