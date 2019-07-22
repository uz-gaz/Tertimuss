class EnvironmentSpecification(object):
    def __init__(self, h: float, t_env: float, t_max: float):
        """
        Specification of the environment

        :param h: Convection factor (W/mm^2 ºC)
        :param t_env: Environment temperature (ºC)
        :param t_max: Maximum temperature (ºC)
        """
        self.h: float = h * (1000 ** 2)
        self.t_env: float = t_env
        self.t_max: float = t_max
