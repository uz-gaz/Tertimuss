from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid


class BoardSpecification(object):
    def __init__(self, physical_properties: MaterialCuboid):
        """
        Board specification

        :param physical_properties: Board physical properties
        """
        self.physical_properties: MaterialCuboid = physical_properties
