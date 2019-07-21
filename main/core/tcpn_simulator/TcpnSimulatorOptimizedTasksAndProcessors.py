import scipy


class TcpnSimulatorOptimizedTasksAndProcessors(object):
    """
    Time continuous petri net simulator used to simulate task and processors
    # WARNING: Actually unused
    """

    def __init__(self, pre: scipy.ndarray, post: scipy.ndarray, pi: scipy.ndarray, lambda_vector: scipy.ndarray,
                 step: float):
        """
        Define the Petri net
        :param pre: pre
        :param post: post
        :param lambda_vector: lambda
        """
        self.__lambda_vector = lambda_vector
        self.__pi = pi
        self.__c = post - pre
        self.__step = step
        self.__a = (self.__c * self.__lambda_vector).dot(self.__pi) * self.__step

    def set_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control
        self.__a = (self.__c * self.__lambda_vector * control).dot(self.__pi) * self.__step

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        flow = (scipy.diag(self.__lambda_vector * self.__control).dot(self.__pi) * self.__step).dot(mo)
        return self.__a.dot(mo) + mo
