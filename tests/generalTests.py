import abc
import unittest
from enum import Enum

# from core.kernel_generator.thermal_model import ThermalModel
# from core.kernel_generator.thermal_model_frequency import ThermalModelFrequencyAware
# from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
# from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
# from core.problem_specification_models.SimulationSpecification import SimulationSpecification
# from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask


class Foo:
    @staticmethod
    @abc.abstractmethod
    def _method_two():
        pass

    @classmethod
    def method_three(cls):
        cls._method_two()


class T2(Foo):
    @staticmethod
    def _method_two():
        print("T2")


class T3(Foo):
    @staticmethod
    def _method_two():
        print("T3")


class T4(Foo):
    def __init__(self):
        print("En el init")

    @staticmethod
    def _method_two():
        print("T3")


class TestSelector(Enum):
    """
    Select thermal model type
    """
    THERMAL_MODEL_ENERGY_BASED = T4
    THERMAL_MODEL_FREQUENCY_BASED = T3


class MyTestCase(unittest.TestCase):
    # def test_something(self):
    #     a_test = T2()
    #     b_test: Foo = T2()
    #
    #     a_test.method_three()
    #     b_test.method_three()
    #
    # def test_thermal_nuevo(self):
    #     tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
    #                                                                   PeriodicTask(3, 8, 8, 8),
    #                                                                   PeriodicTask(3, 12, 12, 9.6)])
    #     cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
    #                                                            MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
    #                                                            2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])
    #
    #     environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)
    #
    #     simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)
    #
    #     thermalModel: ThermalModel = ThermalModelFrequencyAware(tasks_specification, cpu_specification,
    #                                                             environment_specification, simulation_specification)
    #
    #     post, lambda_vector, p_board, p_one_micro = thermalModel.post_sis, thermalModel.lambda_vector_sis, \
    #                                                 thermalModel.p_board, thermalModel.p_one_micro
    #
    #     post, lambda_vector = thermalModel.change_frequency([0.5, 0.5], post, lambda_vector, cpu_specification,
    #                                                         tasks_specification,
    #                                                         p_board, p_one_micro)
    #
    #     pass

    def test_clase_como_variable(self):
        TestSelector.THERMAL_MODEL_ENERGY_BASED.value()

        pass


if __name__ == '__main__':
    unittest.main()
