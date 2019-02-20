class SimulationSpecification(object):

    def __init__(self, step: float, dt: float):
        self.step = step  # Geometry mesh, mesh step (mm)
        self.dt = dt  # Accuracy (s)
