from core.problem_specification_models.SimulationSpecification import SimulationSpecification


class MaterialCuboid(object):

    def __init__(self, x: float, y: float, z: float, p: float, c_p: float, k: float):
        self.x = x  # X coordinate (m)
        self.y = y  # Y coordinate (m)
        self.z = z  # Z coordinate (m)
        self.p = p  # Density (Kg/cm^3)
        self.c_p = c_p  # Specific heat capacities (J/Kg K)
        self.k = k  # Thermal conductivity (W/m ºC)


class Origin(object):

    def __init__(self, x: float, y: float):
        self.x = x  # X coordinate (m)
        self.y = y  # Y coordinate (m)


class CoreSpecification(object):

    def __init__(self, cpu_core: MaterialCuboid, clock_frequency: float, origin: Origin):
        self.cpu_core = cpu_core  # Spec of core
        self.clock_frequency = clock_frequency  # Frequency
        self.origin = origin  # Origin position of core


class CpuSpecification(object):

    def __init__(self, board: MaterialCuboid, cpu_core: MaterialCuboid, number_of_cores: int, clock_frequency: float):
        self.board = board  # Spec of board
        self.cpu_core = cpu_core  # Spec of homogeneous CPU core
        self.number_of_cores = number_of_cores  # Number of homogeneous CPU cores
        self.clock_frequency = clock_frequency  # Frequency of homogeneous CPU cores
        # TODO: Check if is necessary that board/cpu_core x, y, z parameters becomes x/step, y/step, z/step

    '''
        # Constructor for heterogeneous CPU cores  
        def __init__(self, board: MaterialCuboid, cpu_cores: list):
            self.board = board  # Spec of board
            self.cpu_cores = cpu_cores  # Spec of heterogeneous CPU cores
        
    '''

    def get_origins(self, simulation_spec: SimulationSpecification) -> list:
        x = self.board.x / simulation_spec.step
        y = self.board.y / simulation_spec.step
        mx = self.cpu_core.x / simulation_spec.step
        my = self.cpu_core.y / simulation_spec.step
        n = self.number_of_cores
        i = n
        # TODO: Implement function O= n1(x,y,mx,my,n,i)
