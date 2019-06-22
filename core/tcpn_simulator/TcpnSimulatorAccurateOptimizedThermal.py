import scipy


class TcpnSimulatorAccurateOptimizedThermal(object):
    """
    Time continuous petri net simulator
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
        self.limitation_lambda = lambda_vector * step
        self.__a = (self.__c * lambda_vector).dot(self.__pi) * step
        self.__lambda = lambda_vector
        self.__step = step

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """

        # Max number of activations for each transition (limited by the actual marking)
        # limitation_marking = self.__pi.dot(mo).reshape(-1)

        # Number of activations for each transition
        # flow = scipy.minimum(self.limitation_lambda, limitation_marking).reshape((-1, 1))

        # Return the next marking
        # return self.__c.dot(flow) + mo
        #flow = (scipy.diag(self.__lambda)).dot(self.__pi).dot(mo) * self.__step
        return self.__a.dot(mo) + mo
