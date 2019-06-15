import unittest

import scipy


class TestPetriNets(unittest.TestCase):

    def simulate_step(self, c, pi, lambda_pn, mo, transition_control):
        f_m = lambda_pn.dot(scipy.diag(transition_control)).dot(pi).dot(mo)
        mo_next = c.dot(f_m) + mo

        return mo_next

    def calculate_pi(self, pre, mo):
        pre_transpose = pre.transpose()
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

    def test_petri_net_advance_conf_1(self):
        pre = scipy.asarray([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 1]
        ])

        post = scipy.asarray([
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
            [0, 1, 0]
        ])

        lambda_pn = scipy.diag([1, 1, 1])

        mo = scipy.asarray([1, 0, 0, 0]).reshape((-1, 1))

        c = post - pre

        for i in range(6):
            mo_next = self.simulate_step(c, self.calculate_pi(pre, mo), lambda_pn, mo, scipy.asarray([1, 1, 1]))
            mo = mo_next

    def test_petri_net_advance_conf_2(self):
        pre = scipy.asarray([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [1, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ])

        post = scipy.asarray([
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        lambda_pn = scipy.diag([1, 1, 1, 1])

        mo = scipy.asarray([3, 0, 0, 1, 3, 0, 0]).reshape((-1, 1))

        c = post - pre

        for i in range(3):
            # 2 transitions for 1
            mo_next = self.simulate_step(c, self.calculate_pi(pre, mo), lambda_pn, mo, [1, 1, 0, 1])
            mo = mo_next

            mo_next = self.simulate_step(c, self.calculate_pi(pre, mo), lambda_pn, mo, [1, 1, 0, 1])
            mo = mo_next

            # 2 transitions for 3
            mo_next = self.simulate_step(c, self.calculate_pi(pre, mo), lambda_pn, mo, [0, 1, 1, 1])
            mo = mo_next

            mo_next = self.simulate_step(c, self.calculate_pi(pre, mo), lambda_pn, mo, [0, 1, 1, 1])
            mo = mo_next
