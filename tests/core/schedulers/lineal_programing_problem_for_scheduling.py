import hashlib
import unittest

from core.kernel_generator.thermal_model import ThermalModel, generate_thermal_model
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task
from core.schedulers.utils.lineal_programing_problem_for_scheduling import \
    solve_lineal_programing_problem_for_scheduling


class TestLinealProgramingProblem(unittest.TestCase):

    def test_lineal_programing_problem_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([Task(2, 4, 6.4),
                                                                      Task(3, 8, 8),
                                                                      Task(3, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1)

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                             environment_specification,
                                                             simulation_specification)

        # Thermal
        j_b_i, j_fsc_i, quantum, m_t = solve_lineal_programing_problem_for_scheduling(tasks_specification,
                                                                                      cpu_specification,
                                                                                      environment_specification,
                                                                                      simulation_specification,
                                                                                      thermal_model)

        self.assertEqual(hashlib.md5(j_b_i).hexdigest(), "0c1b881becb09cb39f9b105f59e446ba")
        self.assertEqual(hashlib.md5(j_fsc_i).hexdigest(), "1431d18620d5559b1f18c0292ccdf1f0")
        self.assertEqual(hashlib.md5(quantum).hexdigest(), "ac913309c06636286a80a518cbb303f5")
        self.assertEqual(hashlib.md5(m_t).hexdigest(), "9315393e20547da55f4376c4be1a174e")

        # No thermal
        j_b_i, j_fsc_i, quantum, m_t = solve_lineal_programing_problem_for_scheduling(tasks_specification,
                                                                                      cpu_specification,
                                                                                      environment_specification,
                                                                                      simulation_specification,
                                                                                      None)

        self.assertEqual(hashlib.md5(j_b_i).hexdigest(), "0c1b881becb09cb39f9b105f59e446ba")
        self.assertEqual(hashlib.md5(j_fsc_i).hexdigest(), "1431d18620d5559b1f18c0292ccdf1f0")
        self.assertEqual(hashlib.md5(quantum).hexdigest(), "ac913309c06636286a80a518cbb303f5")
        self.assertEqual(m_t, None)


if __name__ == '__main__':
    unittest.main()
