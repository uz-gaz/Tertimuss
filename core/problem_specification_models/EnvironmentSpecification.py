class EnvironmentSpecification(object):

    def __init__(self, h: float, t_env: float, t_max: float):
        self.h = h  # h (W/mm^2 ºC)
        self.t_env = t_env  # Environment temperature (ºC)
        self.t_max = t_max  # Maximum temperature (ºC)
