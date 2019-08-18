from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask

import unittest

from main.core.tcpn_model_generator.TasksModel import TasksModel


class TestTaskModel(unittest.TestCase):

    def test_processor_model(self):
        tasks = [PeriodicTask(2000000, 4, 4, 6.4), PeriodicTask(5000000, 8, 8, 8), PeriodicTask(6000000, 12, 12, 9.6)]

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150000, 400000, 600000, 850000, 1000000],
                                                    [1000000, 1000000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01, True)

        task_model: TasksModel = TasksModel(tasks_specification,
                                            CpuSpecification(board_specification, core_specification),
                                            simulation_specification)

    def test_processor_model_with_aperiodic(self):
        tasks = [PeriodicTask(2000000, 4, 4, 6.4), PeriodicTask(5000000, 8, 8, 8), PeriodicTask(6000000, 12, 12, 9.6),
                 AperiodicTask(1000000, 10, 20, 6)]

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150000, 400000, 600000, 850000, 1000000],
                                                    [1000000, 1000000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01, True)

        task_model: TasksModel = TasksModel(tasks_specification,
                                            CpuSpecification(board_specification, core_specification),
                                            simulation_specification)


if __name__ == '__main__':
    unittest.main()
