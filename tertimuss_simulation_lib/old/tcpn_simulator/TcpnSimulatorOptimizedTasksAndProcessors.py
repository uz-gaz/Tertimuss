import numpy
import scipy.sparse

from .AbstractTcpnSimulator import AbstractTcpnSimulator


class TcpnSimulatorOptimizedTasksAndProcessors(AbstractTcpnSimulator):
    """
    Time continuous Petri net simulator based on the Euler method and optimized to the tasks and processors simulation
    """

    def __init__(self, pre: scipy.sparse.csr_matrix, post: scipy.sparse.csr_matrix, pi: scipy.sparse.csr_matrix,
                 lambda_vector: numpy.ndarray, number_of_steps: int, dt: float):
        """
        Define the TCPN
        :param pre: pre matrix
        :param post: post matrix
        :param pi: pi matrix
        :param lambda_vector: lambda vector
        :param number_of_steps: number of steps in the integration
        :param dt: to solve the state equation, it will be integrated in the interval [0, dt]
        """
        self.__lambda_vector: numpy.ndarray = lambda_vector
        self.__control: numpy.ndarray = numpy.ones(len(lambda_vector))
        self.__pi: scipy.sparse.csr_matrix = pi
        self.__c: scipy.sparse.csr_matrix = post - pre
        self.__dt: float = dt
        self.__number_of_steps: int = number_of_steps

        a: scipy.sparse.csr_matrix = self.__calculate_a(self.__c, self.__lambda_vector, self.__pi,
                                                        self.__dt / self.__number_of_steps)

        self.__a_multi_step: numpy.ndarray = scipy.linalg.fractional_matrix_power(
            (a + scipy.sparse.identity(a.shape[0], dtype=a.dtype, format="csr")).toarray(),
            self.__number_of_steps)

    def set_control(self, control: numpy.ndarray):
        """
        Apply a control action over transitions firing in the TCPN
        :param control: control
        """
        self.__control = control
        a = self.__calculate_a(self.__c, self.__lambda_vector * control, self.__pi, self.__dt / self.__number_of_steps)

        self.__a_multi_step: numpy.ndarray = scipy.linalg.fractional_matrix_power(
            (a + scipy.sparse.identity(a.shape[0], dtype=a.dtype, format="csr")).toarray(),
            self.__number_of_steps)

    @staticmethod
    def __calculate_a(c: scipy.sparse.csr_matrix, lambda_vector: numpy.ndarray, pi: scipy.sparse.csr_matrix,
                      fragmented_dt: float) -> scipy.sparse.csr_matrix:
        """
        Calculate a matrix
        """
        return (c.dot(scipy.sparse.diags(lambda_vector.reshape(-1)))).dot(pi) * fragmented_dt

    def simulate_step(self, mo: numpy.ndarray) -> numpy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        return self.__a_multi_step.dot(mo)
