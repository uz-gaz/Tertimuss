import scipy
import scipy.sparse
import scipy.linalg


class TcpnSimulatorAccurateOptimizedThermal(object):
    """
    Time continuous petri net simulator optimized to simulate thermal
    """

    def __init__(self, pre: scipy.sparse.csr_matrix, post: scipy.sparse.csr_matrix, pi: scipy.sparse.csr_matrix,
                 lambda_vector: scipy.ndarray, step: float, multi_step_number: int):
        """
        Define the Petri net
        :param pre: pre
        :param post: post
        :param lambda_vector: lambda
        """
        self.__pi: scipy.sparse.csr_matrix = pi
        self.__c: scipy.sparse.csr_matrix = post - pre
        self.__pre: scipy.sparse.csr_matrix = pre
        self.__lambda = lambda_vector
        self.__step = step
        self.__multi_step_number = multi_step_number

        a = (self.__c.dot(scipy.sparse.diags(self.__lambda.reshape(-1)))).dot(self.__pi) * self.__step

        self.__a_multi_step: scipy.ndarray = scipy.linalg.fractional_matrix_power(
            a.toarray() + scipy.identity(a.shape[0]),
            self.__multi_step_number)

    def set_post_and_lambda(self, post: scipy.ndarray, lambda_vector: scipy.ndarray):
        """
        Change petri net post and lambda
        """
        self.__c = post - self.__pre
        self.__lambda = lambda_vector

        a = (self.__c.dot(scipy.sparse.diags(self.__lambda.reshape(-1)))).dot(self.__pi) * self.__step

        self.__a_multi_step: scipy.ndarray = scipy.linalg.fractional_matrix_power(
            a.toarray() + scipy.identity(a.shape[0]),
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

    def simulate_multi_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate multi_step_number steps

        :param mo:  actual marking
        :return: next marking
        """
        return self.__a_multi_step.dot(mo)
