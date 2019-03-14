class EnvironmentSpecification(object):

    def __init__(self, h: float, t_env: float, t_max: float):
        self.h = h * (1000 * 1000)  # Convection factor (W/mm^2 ºC) TODO: Check final measurement units
        self.t_env = t_env  # Environment temperature (ºC)
        self.t_max = t_max  # Maximum temperature (ºC)
