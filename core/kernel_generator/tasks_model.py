import scipy

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class TasksModel(object):
    """
        Represents the Task arrival and CPU'S Module in the paper
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):

        n = len(tasks_specification.tasks)
        m = cpu_specification.number_of_cores

        # total of places of the TCPN ((p^w_i,p^cc_i) for each task)
        p = 2 * n

        # Total of transitions ((t^w_i and ti,jAlloc for each processor) for each task)
        t = n + n * m

        # n transitions of tasks period and n * m transitions alloc ((ti,jAlloc for each processor) for each task)
        t_alloc = n * m

        # Incidence Matrix C
        pre = scipy.zeros((p, t))
        post = scipy.zeros((p, t))
        pre_alloc = scipy.zeros((p, t_alloc))
        post_alloc = scipy.zeros((p, t_alloc))
        lambda_vector = scipy.zeros(t)
        pi = scipy.zeros((t, p))
        mo = scipy.zeros((p, 1))

        # Construction of Pre an Post matrix for places(p^w_i,p^cc_i) and transition(t^w_i)
        for k in range(n):
            i = 2 * k
            pre[i, k] = 1  # Transition from p^w_i to t^w_i
            post[i:i + 2, k] = [1,
                                tasks_specification.tasks[k].c]  # Transition from t^w_i to p^w_i, from t^w_i to p^cc_i
            lambda_vector[k] = 1 / tasks_specification.tasks[k].t
            pi[k, i] = 1
            mo[i: i + 2, 0] = [1, tasks_specification.tasks[k].c]

            # Construction of Pre an Post matrix for Transitions alloc
            for r in range(m):
                j = n + r * n + k
                pre[i + 1, j] = 1
                pi[j, i + 1] = 1

        pre_alloc[:, 0: t_alloc] = pre[:, n: t]

        c = post - pre
        c_alloc = post_alloc - pre_alloc
        lambda_tau = scipy.diag(lambda_vector)

        # TODO: Convert to SPARSE MATRIXES
        # Definition of task model
        self.pre_tau = pre
        self.post_tau = post
        self.lambda_vector_tau = lambda_vector
        self.mo_tau = mo
        self.pi_tau = pi

        # Definition of the union between the task model and the processor model
        self.pre_alloc_tau = pre
        self.post_alloc_tau = post
        self.lambda_vector_alloc_tau = lambda_vector
        self.pi_alloc_tau = pi

        # self.c_tau = c
        # self.lambda_tau = lambda_tau

        # self.c_tau_alloc = c_alloc
        # self.m_tau_o = mo
