import math

from core.problem_specification_models.SimulationSpecification import SimulationSpecification


class MaterialCuboid(object):

    def __init__(self, x: float, y: float, z: float, p: float, c_p: float, k: float):
        self.x = x  # X coordinate (mm)
        self.y = y  # Y coordinate (mm)
        self.z = z  # Z coordinate (mm)
        self.p = p  # Density (Kg/cm^3)
        self.c_p = c_p  # Specific heat capacities (J/Kg K)
        self.k = k  # Thermal conductivity (W/m ºC)


class Origin(object):

    def __init__(self, x: float, y: float):
        self.x = x  # X coordinate (mm)
        self.y = y  # Y coordinate (mm)


class CoreSpecification(object):

    def __init__(self, cpu_core: MaterialCuboid, clock_frequency: float, origin: Origin):
        self.cpu_core = cpu_core  # Spec of core
        self.clock_frequency = clock_frequency  # Frequency
        self.origin = origin  # Origin position of core


class CpuSpecification(object):

    # TODO: Check if is necessary that board/cpu_core x, y, z parameters becomes x/step, y/step, z/step

    def __init__(self, board: MaterialCuboid, cpu_core: MaterialCuboid, number_of_cores: int, clock_frequency: float):
        self.board = board  # Spec of board
        self.cpu_core = cpu_core  # Spec of homogeneous CPU core
        self.number_of_cores = number_of_cores  # Number of homogeneous CPU cores
        self.clock_frequency = clock_frequency  # Frequency of homogeneous CPU cores

        def generate_automatic_origins(x0: float, x1: float, y0: float, y1: float, mx: float, my: float,
                                       n: int) -> list:
            # Distribute CPUs in a symmetrical way
            if n == 1:
                return [Origin(x0 + (x1 - x0 - mx) / 2, y0 + (y1 - y0 - my) / 2)]
            else:
                if (x1 - x0) >= (y1 - y0):
                    return generate_automatic_origins(x0, x0 + (x1 - x0) / 2, y0, y1, mx, my, math.ceil(n / 2)) + \
                           generate_automatic_origins(x0 + (x1 - x0) / 2, x1, y0, y1, mx, my, math.floor(n / 2))
                else:
                    return generate_automatic_origins(x0, x1, y0, y0 + (y1 - y0) / 2, mx, my, math.ceil(n / 2)) + \
                           generate_automatic_origins(x0, x1, y0 + (y1 - y0) / 2, y1, mx, my, math.floor(n / 2))

        self.cpu_origins = generate_automatic_origins(0, self.board.x, 0, self.board.y, self.cpu_core.x,
                                                      self.cpu_core.y, self.number_of_cores)

    '''
        # Constructor for heterogeneous CPU cores  
        def __init__(self, board: MaterialCuboid, cpu_cores: list):
            self.board = board  # Spec of board
            self.cpu_cores = cpu_cores  # Spec of heterogeneous CPU cores
        
    '''

    def coordinates(self, simulation_specification: SimulationSpecification) -> list:
        return self.cpu_origins
