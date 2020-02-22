import numpy
import scipy.linalg
import scipy.sparse

class TcpnSimulatorAccurateOptimizedThermal(object):
    """
    Time continuous Petri net simulator based on the Euler method and optimized to the thermal simulation
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
        self.__pi: scipy.sparse.csr_matrix = pi
        self.__c: scipy.sparse.csr_matrix = post - pre
        self.__pre: scipy.sparse.csr_matrix = pre
        self.__lambda = lambda_vector
        self.__step = dt
        self.__multi_step_number = number_of_steps

        a = (self.__c.dot(scipy.sparse.diags(self.__lambda.reshape(-1)))).dot(self.__pi) * (
                    self.__step / self.__multi_step_number)

        self.__a_multi_step: numpy.ndarray = scipy.linalg.fractional_matrix_power(
            (a + scipy.sparse.identity(a.shape[0], dtype=a.dtype, format="csr")).toarray(),
            self.__multi_step_number)

    def set_post_and_lambda(self, post: numpy.ndarray, lambda_vector: numpy.ndarray):
        """
        Change petri net post and lambda
        """
        self.__c = post - self.__pre
        self.__lambda = lambda_vector

        a = (self.__c.dot(scipy.sparse.diags(self.__lambda.reshape(-1)))).dot(self.__pi) * (
                    self.__step / self.__multi_step_number)

        self.__a_multi_step: numpy.ndarray = scipy.linalg.fractional_matrix_power(
            (a + scipy.sparse.identity(a.shape[0], dtype=a.dtype, format="csr")).toarray(),
            self.__multi_step_number)

    def get_post(self):
        """
        Get post matrix
        :return:
        """
        return self.__c + self.__pre

    def get_lambda(self):
        """
        Get lambda vector
        :return:
        """
        return self.__lambda

    def get_a_multi_step(self):
        """
        Get a multi step (Only for debug purposes)
        :return:
        """
        return self.__a_multi_step

    def simulate_multi_step(self, mo: numpy.ndarray) -> numpy.ndarray:
        """
        Simulate multi_step_number steps

        :param mo:  actual marking
        :return: next marking
        """
        return self.__a_multi_step.dot(mo)
