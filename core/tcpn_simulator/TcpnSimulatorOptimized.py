import scipy


class TcpnSimulatorOptimized(object):
    """
    Time continuous petri net simulator
    # TODO: Add check to shapes
    """

    def __init__(self, pre: scipy.ndarray, post: scipy.ndarray, lambda_vector: scipy.ndarray):
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
        self.__c = self.__post - self.__pre
        self.__pre_inv = scipy.vectorize(lambda x: scipy.nan if x == 0 else 1 / x)(pre)

    def change_pre(self, pre: scipy.ndarray):
        """
        Change pre value
        :param pre: pre
        """
        self.__pre = pre
        self.__c = self.__post - self.__pre
        self.__pre_inv = scipy.array(map(lambda x: 0 if x == 0 else 1 / x, pre))

    def change_post(self, post: scipy.ndarray):
        """
        Change post value
        :param post: post
        """
        self.__post = post
        self.__c = self.__post - self.__pre

    def change_lambda(self, lambda_vector: scipy.ndarray):
        """
        Change lambda value
        :param lambda_vector: lambda
        """
        self.__lambda_vector = lambda_vector

    def apply_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control

    def simulate_step(self, mo: scipy.ndarray, step: float) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :param step: step size
        :return: next marking
        """
        # Max number of activations for each transition (limited by the actual control, the lambda and the step)
        limitation_lambda = self.__lambda_vector * self.__control * step

        # Max number of activations for each transition (limited by the actual marking
        limitation_marking = scipy.nanmin(self.__pre_inv * mo, axis=0)

        # It is only necessary if there are transitions without inputs
        # TODO: Add check
        # limitation_marking = scipy.vectorize(lambda x: 0 if x == scipy.nan else x)(limitation_marking)

        # Number of activations for each transition
        flow = scipy.minimum(limitation_lambda, limitation_marking).reshape((-1, 1))

        # Return the next marking
        return self.__c.dot(flow) + mo
