import scipy


class TcpnSimulatorAccurateOptimizedTasks(object):
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
        self.__pre = pre
        self.__post = post
        self.__lambda_vector = lambda_vector
        self.__control = scipy.ones(len(lambda_vector))
        self.__pi = pi
        self.__c = self.__post - self.__pre
        self.__step = step
        self.__calculate_constant_values()

    def set_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control
        self.__calculate_constant_values()

    def __calculate_constant_values(self):
        """
        Calculate all constant values during the simulation
        """
        # Max number of activations for each transition (limited by the actual control, the lambda and the step)
        self.limitation_lambda = self.__lambda_vector * self.__control * self.__step

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        pi = self.__pi

        # Max number of activations for each transition (limited by the actual marking)
        limitation_marking = pi.dot(mo).reshape(-1)

        # Number of activations for each transition
        flow = scipy.minimum(self.limitation_lambda, limitation_marking).reshape((-1, 1))

        # Return the next marking
        return self.__c.dot(flow) + mo
