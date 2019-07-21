from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.cpu_specification.Origin import Origin


class CoreSpecification(object):
    """
    Spec of a core
    """

    def __init__(self, cpu_core: MaterialCuboid, clock_frequency: float, origin: Origin):
        """

        :param cpu_core: Spec of core
        :param clock_frequency: Frequency
        :param origin: Origin position of core
        """
        self.cpu_core = cpu_core
        self.clock_frequency = clock_frequency
        self.origin = origin