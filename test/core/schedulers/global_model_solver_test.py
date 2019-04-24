import time
import unittest

import scipy
import scipy.integrate

from core.kernel_generator.global_model import generate_global_model, GlobalModel
from core.kernel_generator.processor_model import generate_processor_model, ProcessorModel
from core.kernel_generator.tasks_model import TasksModel, generate_tasks_model
from core.kernel_generator.thermal_model import ThermalModel, generate_thermal_model
from core.problem_specification_models.CpuSpecification import MaterialCuboid, CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task


class GlobalModelSolver(unittest.TestCase):
    def solve_global_model(self, global_model: GlobalModel, mo: scipy.ndarray, w_alloc: scipy.ndarray, ma: float,
                           time_sol: scipy.ndarray) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                        scipy.ndarray, scipy.ndarray,
                                                        scipy.ndarray, scipy.ndarray]:
        aux = global_model.b.dot(w_alloc) + global_model.bp.reshape(-1) * ma
        res = scipy.integrate.solve_ivp(lambda t, m: global_model.a.dot(m.transpose()) + aux, time_sol, mo,
                                        dense_output=True)

        m_m = res.y.transpose()[- 1]

        y_m = global_model.s.dot(m_m)

        temp_time = global_model.s.dot(res.y)[2 * len(w_alloc): len(y_m), :]

        m_busy = y_m[0:len(w_alloc)]
        m_exec = y_m[len(w_alloc): 2 * len(w_alloc)]
        temp = y_m[2 * len(w_alloc): len(y_m)]

        return m_m.reshape((-1, 1)), m_exec.reshape((-1, 1)), m_busy.reshape((-1, 1)), temp.reshape(
            (-1, 1)), res.t.reshape((-1, 1)), temp_time, res.y

    def solve_global_model_2(self, global_model: GlobalModel, mo: scipy.ndarray, w_alloc: scipy.ndarray, ma: float,
                             time_sol: scipy.ndarray) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                          scipy.ndarray, scipy.ndarray,
                                                          scipy.ndarray, scipy.ndarray]:
        res = scipy.integrate.RK45(
            lambda t, m: global_model.a.dot(m.transpose()) + global_model.b.dot(w_alloc) + global_model.bp.reshape(
                -1) * ma,
            time_sol[0], mo, time_sol[1]
        )  # FIXME: In matlab ode 45 always return x*45 matrix

        m_m = res.y.transpose()[- 1]

        y_m = global_model.s.dot(m_m)

        t_aux = global_model.s.dot(res.y)

        temp_time = t_aux[2 * len(w_alloc): len(y_m), :]

        m_busy = y_m[0:len(w_alloc)]
        m_exec = y_m[len(w_alloc): 2 * len(w_alloc)]
        temp = y_m[2 * len(w_alloc): len(y_m)]

        return m_m.reshape((-1, 1)), m_exec.reshape((-1, 1)), m_busy.reshape((-1, 1)), temp.reshape(
            (-1, 1)), res.t.reshape((-1, 1)), temp_time, res.y

    def test_global_model_solver(self):
        mo = [1, 2, 1, 3, 1, 3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1] + 675 * [45]

        mo = scipy.asarray(mo)

        # TimeSol: scipy.ndarray = scipy.asarray([0, 0.5])
        # TimeSol = TimeSol.reshape((len(TimeSol), 1))
        # TimeSol = scipy.linspace(0, 0.5, 45)
        TimeSol = [0, 0.5]

        ma: float = 45

        w_alloc: scipy.ndarray = scipy.asarray(
            [0.250000000000003, 0.187500000000001, 0.125000000000000, 0.250000000000001, 0.187500000000001,
             0.125000000000000])

        tasks_specification: TasksSpecification = TasksSpecification([Task(2, 4, 6.4),
                                                                      Task(3, 8, 8),
                                                                      Task(3, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1)

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

        tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

        thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                             environment_specification,
                                                             simulation_specification)

        # time_0 = time.time()

        global_model, _ = generate_global_model(tasks_model, processor_model, thermal_model,
                                                environment_specification)

        # for i in range(20):
        m, m_exec, m_busy, temp, tout, temp_time, m_tcpn = self.solve_global_model(global_model, mo, w_alloc, ma,
                                                                                   TimeSol)

        # time_1 = time.time()

        # print(time_1 - time_0)


if __name__ == '__main__':
    unittest.main()
