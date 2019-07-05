import unittest
import scipy.io as sio
import scipy.optimize
import scipy.linalg
from core.schedulers.implementations.global_wodes import GlobalWodesScheduler
import pulp


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # a_eq_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/wodes_aeq.mat')['Aeq']
        # a_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/wodes_a.mat')['A']
        # b_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/wodes_b.mat')['b']
        # b_eq_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/wodes_beq.mat')['beq']
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        gw = GlobalWodesScheduler()
        gw.ilpp_dp(ci, ti, 3, 2)

    def test_something_2(self):
        a_eq_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/Aeq.mat')['Aeq']
        a_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/A.mat')['A']
        b_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/b.mat')['b']
        b_eq_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/beq.mat')['beq']
        f_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/F.mat')['F']
        pass

        def rank(matrix_to_calculate):
            u, s, v = scipy.linalg.svd(matrix_to_calculate)
            return scipy.sum(s > 1e-10)

        print(rank(a_matlab))
        print(rank(b_matlab))
        print(rank(a_eq_matlab))
        print(rank(b_eq_matlab))

        res = scipy.optimize.linprog(c=f_matlab, A_ub=a_matlab, b_ub=b_matlab, A_eq=a_eq_matlab,
                                     b_eq=b_eq_matlab, method='simplex')

        pass

    def test_something_3(self):
        a_eq_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/Aeq.mat')['Aeq']
        a_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/A.mat')['A']
        b_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/b.mat')['b']
        b_eq_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/beq.mat')['beq']
        f_matlab = sio.loadmat('/home/achils/Documentos/University/TFG/tests/core/schedulers/F.mat')['F']

        problem = pulp.LpProblem("problemName", pulp.LpMinimize)


if __name__ == '__main__':
    unittest.main()
