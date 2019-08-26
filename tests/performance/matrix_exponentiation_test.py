import time
import unittest

import numpy
import scipy

from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.tcpn_model_generator.ThermalModelFrequency import ThermalModelFrequencyAware
import scipy.sparse


class MatrixExponentiationTest(unittest.TestCase):
    @staticmethod
    def __obtain_matrix_to_exponentiation(dt: float = 2, dt_fragmentation: int = 128) -> [scipy.ndarray]:
        """
        Generate global model
        :return: global model, step, simulations each step, number of steps
        """
        # Problem specification
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150, 400, 600, 850, 1000],
                                                    [1000, 1000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(dt, 0.01, True,
                                                                                    dt_fragmentation_thermal=dt_fragmentation)

        cpu_specification = CpuSpecification(board_specification, core_specification)

        thermal_model = ThermalModelFrequencyAware(tasks_specification, cpu_specification, environment_specification,
                                                   simulation_specification)

        c = thermal_model.post_sis - thermal_model.pre_sis

        a = (c.dot(scipy.sparse.diags(thermal_model.lambda_vector_sis.reshape(-1)))).dot(thermal_model.pi_sis) * (
                simulation_specification.dt / simulation_specification.dt_fragmentation_thermal)

        return (a + scipy.sparse.identity(a.shape[0], dtype=a.dtype, format="csr")).toarray()

    def test_scipy_fractional_matrix_power(self):
        to_exp = self.__obtain_matrix_to_exponentiation(1, 128)

        for _ in range(10):
            time_1 = time.time()
            _ = scipy.linalg.fractional_matrix_power(to_exp, 128)
            time_2 = time.time()
            print("Time taken in a exponentiation", time_2 - time_1)

        """
        Time taken in a exponentiation 8.682569742202759
        Time taken in a exponentiation 8.524996042251587
        Time taken in a exponentiation 8.59777545928955
        Time taken in a exponentiation 8.42630648612976
        Time taken in a exponentiation 8.539497375488281
        Time taken in a exponentiation 8.528483152389526
        Time taken in a exponentiation 8.588711977005005
        Time taken in a exponentiation 8.468076944351196
        Time taken in a exponentiation 8.390530824661255
        Time taken in a exponentiation 8.395685195922852
        """

    def test_numpy_matrix_power(self):
        to_exp = self.__obtain_matrix_to_exponentiation(1, 128)

        for _ in range(10):
            time_1 = time.time()
            _ = numpy.linalg.matrix_power(to_exp, 128)
            time_2 = time.time()
            print("Time taken in a exponentiation", time_2 - time_1)

        """
        Time taken in a exponentiation 8.701900005340576
        Time taken in a exponentiation 8.553551197052002
        Time taken in a exponentiation 8.432413578033447
        Time taken in a exponentiation 8.416751384735107
        Time taken in a exponentiation 8.46647572517395
        Time taken in a exponentiation 8.409261703491211
        Time taken in a exponentiation 8.420466899871826
        Time taken in a exponentiation 8.416542530059814
        Time taken in a exponentiation 8.419806718826294
        Time taken in a exponentiation 8.44095230102539
        """


if __name__ == '__main__':
    unittest.main()
