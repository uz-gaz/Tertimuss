class EnvironmentSpecification(object):
    """
    Specification of the environment
    """

    def __init__(self, h: float, t_env: float, t_max: float):
        """

        :param h: Convection factor (W/mm^2 ºC)
        :param t_env: Environment temperature (ºC)
        :param t_max: Maximum temperature (ºC)
        """
        self.h = h * (1000 ** 2)
        self.t_env = t_env
        self.t_max = t_max
