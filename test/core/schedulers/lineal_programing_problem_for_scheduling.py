import unittest

from core.kernel_generator.thermal_model import ThermalModel, generate_thermal_model
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task
from core.schedulers.lineal_programing_problem_for_scheduling import solve_lineal_programing_problem_for_scheduling


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

        solve_lineal_programing_problem_for_scheduling(tasks_specification,
                                                       cpu_specification,
                                                       environment_specification,
                                                       simulation_specification,
                                                       thermal_model)


if __name__ == '__main__':
    unittest.main()
