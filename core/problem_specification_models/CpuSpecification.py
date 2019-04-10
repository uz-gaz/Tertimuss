import math


class MaterialCuboid(object):
    """
    Material object with cuboid' shape
    """

    def __init__(self, x: float, y: float, z: float, p: float, c_p: float, k: float):
        """

        :param x: X coordinate size (mm)
        :param y: Y coordinate size (mm)
        :param z: Z coordinate size (mm)
        :param p: Density (Kg/cm^3)
        :param c_p: Specific heat capacities (J/Kg K)
        :param k: Thermal conductivity (W/m ºC)
        """
        self.x = x
        self.y = y
        self.z = z
        self.p = p
        self.c_p = c_p
        self.k = k


class Origin(object):
    """
    Origins of material cuboid
    """

    def __init__(self, x: float, y: float):
        """

        :param x: X coordinate (mm)
        :param y: Y coordinate (mm)
        """
        self.x = x
        self.y = y


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


class CpuSpecification(object):

    def __init__(self, board: MaterialCuboid, cpu_core: MaterialCuboid, number_of_cores: int, clock_frequency: float):
        self.board = board  # Spec of board
        self.cpu_core = cpu_core  # Spec of homogeneous CPU core
        self.number_of_cores = number_of_cores  # Number of homogeneous CPU cores
        self.clock_frequency = clock_frequency  # Frequency scale of homogeneous CPU cores (1 is the base frequency
        # at which the platform could operate)

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
