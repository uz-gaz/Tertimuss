class SimulationSpecification(object):
    """
    Specification of some parameters of the simulation
    """

    def __init__(self, step: float, dt: float):
        """

        :param step: Geometry mesh, mesh step (mm)
        :param dt:  Accuracy (s)
        """
        self.step = step
        self.dt = dt
