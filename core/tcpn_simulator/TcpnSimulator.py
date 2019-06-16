import scipy


class TcpnSimulator(object):
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

    def change_pre(self, pre: scipy.ndarray):
        """
        Change pre value
        :param pre: pre
        """
        self.__pre = pre

    def change_post(self, post: scipy.ndarray):
        """
        Change post value
        :param post: post
        """
        self.__post = post

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

    def __calculate_pi(self, mo):
        """
        Calculate pi
        :param mo: actual marking
        :return: pi
        """
        pre_transpose = self.__pre.transpose()
        pi = scipy.zeros(pre_transpose.shape)

        for i in range(len(pre_transpose)):
            places = pre_transpose[i]
            max_index = -1
            max_global = 0
            for j in range(len(places)):
                if places[j] != 0:
                    if mo[j] != 0:
                        max_interior = places[j] / mo[j]
                        if max_global < max_interior:
                            max_global = max_interior
                            max_index = j
                    else:
                        max_index = -1
                        break
            if max_index != -1:
                pi[i][max_index] = 1 / places[max_index]

        return pi

    def simulate_step(self, mo: scipy.ndarray, step: float) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :param step: step size
        :return: next marking
        """

        c = self.__post - self.__pre
        pi = self.__calculate_pi(mo)

        # Max number of activations for each transition (limited by the actual control, the lambda and the step)
        limitation_lambda = self.__lambda_vector * self.__control * step

        # Max number of activations for each transition (limited by the actual marking)
        limitation_marking = pi.dot(mo).reshape(-1)

        # Number of activations for each transition
        flow = scipy.minimum(limitation_lambda, limitation_marking).reshape((-1, 1))

        # Return the next marking
        return c.dot(flow) + mo
