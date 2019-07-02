import scipy


class TcpnSimulatorAccurateOptimizedThermal(object):
    """
    Time continuous petri net simulator optimized to simulate thermal
    """

    def __init__(self, pre: scipy.ndarray, post: scipy.ndarray, pi: scipy.ndarray,
                 lambda_vector: scipy.ndarray, step: float):
        """
        Define the Petri net
        :param pre: pre
        :param post: post
        :param lambda_vector: lambda
        """
        self.__pi = pi
        self.__c = post - pre
        self.__a = (self.__c * lambda_vector).dot(self.__pi) * step
        self.__lambda = lambda_vector
        self.__step = step
        self.__lambda_dot_pi = self.__lambda.reshape((-1, 1)) * self.__pi

    def set_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__a = (self.__c * control).dot(self.__lambda_dot_pi) * self.__step

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        return self.__a.dot(mo) + mo
