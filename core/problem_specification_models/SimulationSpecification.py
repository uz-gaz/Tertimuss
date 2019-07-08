from typing import Optional


class SimulationSpecification(object):
    """
    Specification of some parameters of the simulation
    """

    def __init__(self, step: Optional[float], dt: float):
        """

        :param step: Mesh step size (mm)
        :param dt:  Accuracy in seconds
        """
        self.step: Optional[float] = step
        self.dt: float = dt

        # TODO: Put in the specification
        self.dt_fragmentation_proc_task: int = 10
        self.dt_fragmentation_thermal: int = 100

        self.float_round: int = 5
