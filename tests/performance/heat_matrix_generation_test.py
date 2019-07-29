import sys
import time
import unittest

import scipy
import scipy.sparse

from main.core.tcpn_model_generator.global_model import GlobalModel
from main.core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask


class HeatMatrixGeneration(unittest.TestCase):
    @staticmethod
    def __size_of_sparse(matrix_sparse):
        if scipy.sparse.isspmatrix_coo(matrix_sparse):
            return matrix_sparse.data.nbytes + matrix_sparse.col.nbytes + matrix_sparse.row.nbytes
        else:
            return matrix_sparse.data.nbytes + matrix_sparse.indptr.nbytes + matrix_sparse.indices.nbytes

    @classmethod
    def __elevate_sparse(cls, matrix, power: int):
        if power <= 3:
            if power == 1:
                return matrix
            elif power == 2:
                return matrix.dot(matrix)
            elif power == 3:
                return matrix.dot(matrix).dot(matrix)
            else:
                raise Exception("Error: Power must be greater than 0")
        else:
            return cls.__elevate_sparse(matrix, power // 2).dot(
                cls.__elevate_sparse(matrix, (power // 2) + (power % 2)))

    @staticmethod
    def __specification_and_creation_of_the_model() -> [GlobalModel, float, int, int]:
        """
        Generate global model
        :return: global model, step, simulations each step, number of steps
        """
        # Problem specification
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(0.65, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        # Creation of TCPN model
        time_1 = time.time()
        global_model = GlobalModel(global_specification, True)
        time_2 = time.time()

        print("Size of pre and post (each one):", sys.getsizeof(global_model.pre_thermal) / (1024 ** 3), "GB")
        non_zeros_pre = scipy.count_nonzero(global_model.pre_thermal)
        non_zeros_post = scipy.count_nonzero(global_model.post_thermal)
        places_matrix_pre = global_model.pre_thermal.shape[0] * global_model.pre_thermal.shape[1]

        print("Density of pre:", non_zeros_pre / places_matrix_pre)
        print("Density of post:", non_zeros_post / places_matrix_pre)
        print("Time taken creation of the model:", time_2 - time_1)

        """
               Problem with step = 1
               Size of pre and post (each one): 0.2749609798192978 GB
               Density of pre: 0.00036927621861152144
               Density of post: 0.00039095371897028406
               Time taken creation of the model: 4.081545352935791
        """
        return global_model, 0.01, 100, 2000

    def test_heat_matrix_execution_performance_ndarray_one_step(self):
        """
        Simulation of execution with ndarray (no sparse)
        """
        print("Simulation of execution with ndarray (no sparse)")

        global_model, dt, dt_fragmentation, num_simulations = self.__specification_and_creation_of_the_model()

        # TCPN simulator creation
        time_start = time.time()

        pi = global_model.pi_thermal
        pre = global_model.pre_thermal
        c = global_model.post_thermal - global_model.pre_thermal
        lambda_vector = global_model.lambda_vector_thermal
        mo = global_model.mo_thermal

        a = (c * lambda_vector).dot(pi) * (dt / dt_fragmentation)

        print("Time taken creation of the TCPN solver:", time.time() - time_start)

        print("Density of a:", scipy.count_nonzero(a) / (a.shape[0] * a.shape[1]))
        print("Size of a:", sys.getsizeof(a) / (1024 ** 3), "GB")
        print("Size of pre:", sys.getsizeof(pre) / (1024 ** 3), "GB")
        print("Size of c:", sys.getsizeof(c) / (1024 ** 3), "GB")
        print("Size of lambda vector:", sys.getsizeof(lambda_vector) / (1024 ** 3), "GB")
        print("Size of mo:", sys.getsizeof(mo) / (1024 ** 3), "GB")

        del global_model

        time_start = time.time()

        # Simulation of steps
        for _ in range(num_simulations):
            for _ in range(dt_fragmentation):
                mo = a.dot(mo)

        print("Time taken simulating", num_simulations, "steps:", time.time() - time_start)

        """
        Simulation of execution with ndarray (no sparse)
        Time taken creation of the TCPN solver: 6.639012813568115
        Density of a: 0.0023072945416938487
        Size of a: 0.054637178778648376 GB
        Size of pre: 0.2749609798192978 GB
        Size of c: 0.2749609798192978 GB
        Size of lambda vector: 0.00010162591934204102 GB
        Size of mo: 1.043081283569336e-07 GB
        Time taken simulating 2000 steps: 1735.3220582008362
        """

    def test_heat_matrix_execution_performance_ndarray(self):
        """
        Simulation of execution with ndarray (no sparse) and multi step
        """
        print("Simulation of execution with ndarray (no sparse) and multi step")

        global_model, dt, dt_fragmentation, num_simulations = self.__specification_and_creation_of_the_model()

        # TCPN simulator creation
        time_start = time.time()

        pi = global_model.pi_thermal
        pre = global_model.pre_thermal
        c = global_model.post_thermal - global_model.pre_thermal
        lambda_vector = global_model.lambda_vector_thermal
        mo = global_model.mo_thermal

        a = (c * lambda_vector).dot(pi) * (dt / dt_fragmentation)

        a_multi_step = scipy.linalg.fractional_matrix_power(a + scipy.identity(len(a)), dt_fragmentation)

        print("Time taken creation of the TCPN solver:", time.time() - time_start)

        print("Density of a:", scipy.count_nonzero(a) / (a.shape[0] * a.shape[1]))
        print("Density of a multi step:",
              (scipy.count_nonzero(a_multi_step)) / (a_multi_step.shape[0] * a_multi_step.shape[1]))

        print("Size of a:", sys.getsizeof(a) / (1024 ** 3), "GB")
        print("Size of a multi step:", sys.getsizeof(a_multi_step) / (1024 ** 3), "GB")
        print("Size of pre:", sys.getsizeof(pre) / (1024 ** 3), "GB")
        print("Size of c:", sys.getsizeof(c) / (1024 ** 3), "GB")
        print("Size of lambda vector:", sys.getsizeof(lambda_vector) / (1024 ** 3), "GB")
        print("Size of mo:", sys.getsizeof(mo) / (1024 ** 3), "GB")

        del a
        del global_model

        time_start = time.time()

        # Simulation of steps
        for _ in range(num_simulations):
            mo = a_multi_step.dot(mo)

        print("Time taken simulating", num_simulations, "steps:", time.time() - time_start)

        """
        Simulation of execution with ndarray (no sparse) and multi step
        Time taken creation of the TCPN solver: 15.578176259994507
        Density of a: 0.0023072945416938487
        Density of a multi step: 0.9970468811705129
        Size of a: 0.054637178778648376 GB
        Size of a multi step: 0.054637178778648376 GB
        Size of pre: 0.2749609798192978 GB
        Size of c: 0.2749609798192978 GB
        Size of lambda vector: 0.00010162591934204102 GB
        Size of mo: 1.043081283569336e-07 GB
        Time taken simulating 2000 steps: 17.19204545021057
        """

    @classmethod
    def __heat_matrix_execution_performance_sparse_one_step(cls, sparse_matrix_type):
        """
        Simulation of execution with sparse and one step each iteration
        """
        print("Simulation of execution with sparse and one step each iteration")

        global_model, dt, dt_fragmentation, num_simulations = cls.__specification_and_creation_of_the_model()

        # TCPN simulator creation
        time_start = time.time()

        pi = sparse_matrix_type(global_model.pi_thermal)
        pre = sparse_matrix_type(global_model.pre_thermal)
        c = sparse_matrix_type(sparse_matrix_type(global_model.post_thermal) - pre)
        lambda_vector = global_model.lambda_vector_thermal
        mo = sparse_matrix_type(global_model.mo_thermal)

        a = (c.dot(scipy.sparse.diags(lambda_vector.reshape(-1)))).dot(pi) * (dt / dt_fragmentation)

        print("Time taken creation of the TCPN solver:", time.time() - time_start)

        print("Size of pre :", cls.__size_of_sparse(pre) / (1024 ** 3), "GB")
        print("Size of pi :", cls.__size_of_sparse(pi) / (1024 ** 3), "GB")
        print("Size of c :", cls.__size_of_sparse(c) / (1024 ** 3), "GB")
        print("Size of a :", cls.__size_of_sparse(a) / (1024 ** 3), "GB")
        print("Size of lambda_vector:", sys.getsizeof(lambda_vector) / (1024 ** 3), "GB")
        print("Size of mo :", cls.__size_of_sparse(mo) / (1024 ** 3), "GB")

        del global_model

        time_start = time.time()

        # Simulation of steps
        for _ in range(num_simulations):
            for _ in range(dt_fragmentation):
                mo = a.dot(mo)

        print("Time taken simulating", num_simulations, "steps:", time.time() - time_start)

    @classmethod
    def __heat_matrix_generation_and_execution_performance_sparse_multi_step(cls, sparse_matrix_type):
        """
        Simulation of execution with sparse and multi step
        :return:
        """
        print("Simulation of execution with sparse and multi step")

        global_model, dt, dt_fragmentation, num_simulations = cls.__specification_and_creation_of_the_model()

        # TCPN simulator creation
        time_start = time.time()

        pi = sparse_matrix_type(global_model.pi_thermal)
        pre = sparse_matrix_type(global_model.pre_thermal)
        c = sparse_matrix_type(sparse_matrix_type(global_model.post_thermal) - pre)
        lambda_vector = global_model.lambda_vector_thermal
        mo = sparse_matrix_type(global_model.mo_thermal)

        a = (c.dot(scipy.sparse.diags(lambda_vector.reshape(-1)))).dot(pi) * (dt / dt_fragmentation)

        a_multi_step = cls.__elevate_sparse(a + scipy.sparse.identity(a.shape[1]), dt_fragmentation)

        print("Time taken creation of the TCPN solver:", time.time() - time_start)

        print("Size of pre :", cls.__size_of_sparse(pre) / (1024 ** 3), "GB")
        print("Size of pi :", cls.__size_of_sparse(pi) / (1024 ** 3), "GB")
        print("Size of c :", cls.__size_of_sparse(c) / (1024 ** 3), "GB")
        print("Size of a_multi_step :", cls.__size_of_sparse(a_multi_step) / (1024 ** 3), "GB")
        print("Size of lambda_vector:", sys.getsizeof(lambda_vector) / (1024 ** 3), "GB")
        print("Size of mo :", cls.__size_of_sparse(mo) / (1024 ** 3), "GB")

        del global_model
        del a

        time_start = time.time()

        # Simulation of steps
        for _ in range(num_simulations):
            mo = a_multi_step.dot(mo)

        print("Time taken simulating", num_simulations, "steps:", time.time() - time_start)

    def test_heat_matrix_execution_performance_sparse_csr_matrix(self):
        """
        Simulation of execution with sparse csr_matrix
        :return:
        """
        print("")
        sparse_matrix_type = scipy.sparse.csr_matrix
        print("Simulation of execution with sparse csr_matrix")
        self.__heat_matrix_execution_performance_sparse_one_step(sparse_matrix_type)
        print("")
        self.__heat_matrix_generation_and_execution_performance_sparse_multi_step(sparse_matrix_type)
        print("")

        """
        Simulation of execution with sparse csr_matrix
        Simulation of execution with sparse and one step each iteration
        Time taken creation of the TCPN solver: 1.939915418624878
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a : 0.00019918754696846008 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 71.71548199653625
        
        Simulation of execution with sparse and multi step
        Time taken creation of the TCPN solver: 95.79970049858093
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a_multi_step : 0.08172367885708809 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 161.06178998947144
        """

    def test_heat_matrix_execution_performance_sparse_bsr_matrix(self):
        """
        Simulation of execution with sparse bsr_matrix
        :return:
        """
        print("")
        sparse_matrix_type = scipy.sparse.bsr_matrix
        print("Simulation of execution with sparse bsr_matrix")
        self.__heat_matrix_execution_performance_sparse_one_step(sparse_matrix_type)
        print("")
        self.__heat_matrix_generation_and_execution_performance_sparse_multi_step(sparse_matrix_type)
        print("")

        """
        Simulation of execution with sparse bsr_matrix
        Simulation of execution with sparse and one step each iteration
        Time taken creation of the TCPN solver: 1.943782091140747
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a : 0.00019918754696846008 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 73.03531384468079
        
        Simulation of execution with sparse and multi step
        Time taken creation of the TCPN solver: 95.99418210983276
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a_multi_step : 0.08172367885708809 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 213.35230422019958
        """

    def test_heat_matrix_execution_performance_sparse_coo_matrix(self):
        """
        Simulation of execution with sparse coo_matrix
        :return:
        """
        print("")
        sparse_matrix_type = scipy.sparse.coo_matrix
        print("Simulation of execution with sparse coo_matrix")
        self.__heat_matrix_execution_performance_sparse_one_step(sparse_matrix_type)
        print("")
        self.__heat_matrix_generation_and_execution_performance_sparse_multi_step(sparse_matrix_type)
        print("")

        """
        Simulation of execution with sparse coo_matrix
        Simulation of execution with sparse and one step each iteration
        Time taken creation of the TCPN solver: 1.9422714710235596
        Size of pre : 0.00020307302474975586 GB
        Size of pi : 0.00020307302474975586 GB
        Size of c : 0.00041484832763671875 GB
        Size of a : 0.00019918754696846008 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.026293754577637e-05 GB
        Time taken simulating 2000 steps: 71.44981169700623
        
        Simulation of execution with sparse and multi step
        Time taken creation of the TCPN solver: 95.82761478424072
        Size of pre : 0.00020307302474975586 GB
        Size of pi : 0.00020307302474975586 GB
        Size of c : 0.00041484832763671875 GB
        Size of a_multi_step : 0.08172367885708809 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.026293754577637e-05 GB
        Time taken simulating 2000 steps: 160.919025182724
        """

    def test_heat_matrix_execution_performance_sparse_csc_matrix(self):
        """
        Simulation of execution with sparse csc_matrix
        :return:
        """
        print("")
        sparse_matrix_type = scipy.sparse.csr_matrix
        print("Simulation of execution with sparse csc_matrix")
        self.__heat_matrix_execution_performance_sparse_one_step(sparse_matrix_type)
        print("")
        self.__heat_matrix_generation_and_execution_performance_sparse_multi_step(sparse_matrix_type)
        print("")

        """
        Simulation of execution with sparse csc_matrix
        Simulation of execution with sparse and one step each iteration
        Time taken creation of the TCPN solver: 1.9407780170440674
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a : 0.00019918754696846008 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 71.53424167633057
        
        Simulation of execution with sparse and multi step
        Time taken creation of the TCPN solver: 95.66145586967468
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a_multi_step : 0.08172367885708809 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 161.04035997390747
        """

    def test_heat_matrix_execution_performance_sparse_dia_matrix(self):
        """
        Simulation of execution with sparse csr_matrix
        :return:
        """
        print("")
        sparse_matrix_type = scipy.sparse.csr_matrix
        print("Simulation of execution with sparse dia_matrix")
        self.__heat_matrix_execution_performance_sparse_one_step(sparse_matrix_type)
        print("")
        self.__heat_matrix_generation_and_execution_performance_sparse_multi_step(sparse_matrix_type)
        print("")

        """
        Simulation of execution with sparse dia_matrix
        Simulation of execution with sparse and one step each iteration
        Time taken creation of the TCPN solver: 1.9404592514038086
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a : 0.00019918754696846008 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 71.50228977203369
        
        Simulation of execution with sparse and multi step
        Time taken creation of the TCPN solver: 95.71642279624939
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a_multi_step : 0.08172367885708809 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 160.96726632118225
        """

    def test_heat_matrix_execution_performance_sparse_dok_matrix(self):
        """
        Simulation of execution with sparse csr_matrix
        :return:
        """
        print("")
        sparse_matrix_type = scipy.sparse.csr_matrix
        print("Simulation of execution with sparse dok_matrix")
        self.__heat_matrix_execution_performance_sparse_one_step(sparse_matrix_type)
        print("")
        self.__heat_matrix_generation_and_execution_performance_sparse_multi_step(sparse_matrix_type)
        print("")

        """
        Simulation of execution with sparse dok_matrix
        Simulation of execution with sparse and one step each iteration
        Time taken creation of the TCPN solver: 1.939544439315796
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a : 0.00019918754696846008 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 71.58235740661621
        
        Simulation of execution with sparse and multi step
        Time taken creation of the TCPN solver: 95.72665667533875
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a_multi_step : 0.08172367885708809 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 160.99669289588928
        """

    def test_heat_matrix_execution_performance_sparse_lil_matrix(self):
        """
        Simulation of execution with sparse csr_matrix
        :return:
        """
        print("")
        sparse_matrix_type = scipy.sparse.csr_matrix
        print("Simulation of execution with sparse lil_matrix")
        self.__heat_matrix_execution_performance_sparse_one_step(sparse_matrix_type)
        print("")
        self.__heat_matrix_generation_and_execution_performance_sparse_multi_step(sparse_matrix_type)
        print("")

        """
        Simulation of execution with sparse lil_matrix
        Simulation of execution with sparse and one step each iteration
        Time taken creation of the TCPN solver: 1.941390037536621
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a : 0.00019918754696846008 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 71.56469798088074
        
        Simulation of execution with sparse and multi step
        Time taken creation of the TCPN solver: 95.6835708618164
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a_multi_step : 0.08172367885708809 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 4.02890145778656e-05 GB
        Time taken simulating 2000 steps: 161.00649881362915
        """

    def test_heat_matrix_execution_performance_sparse_none_sparse_multi_step(self):
        """
        Simulation of execution with sparse and one step each iteration
        """
        print("Simulation of execution with sparse and none sparse mix")

        global_model, dt, dt_fragmentation, num_simulations = self.__specification_and_creation_of_the_model()

        sparse_matrix_type = scipy.sparse.csr_matrix

        # TCPN simulator creation
        time_start = time.time()

        pi = sparse_matrix_type(global_model.pi_thermal)
        pre = sparse_matrix_type(global_model.pre_thermal)
        c = sparse_matrix_type(sparse_matrix_type(global_model.post_thermal) - pre)
        lambda_vector = global_model.lambda_vector_thermal
        mo = global_model.mo_thermal

        del global_model

        a = (c.dot(scipy.sparse.diags(lambda_vector.reshape(-1)))).dot(pi) * (dt / dt_fragmentation)
        a = a.toarray()

        a_multi_step = scipy.linalg.fractional_matrix_power(a + scipy.identity(len(a)), dt_fragmentation)

        print("Time taken creation of the TCPN solver:", time.time() - time_start)

        print("Size of pre :", self.__size_of_sparse(pre) / (1024 ** 3), "GB")
        print("Size of pi :", self.__size_of_sparse(pi) / (1024 ** 3), "GB")
        print("Size of c :", self.__size_of_sparse(c) / (1024 ** 3), "GB")
        print("Size of a :", sys.getsizeof(a) / (1024 ** 3), "GB")
        print("Size of a multi-step:", sys.getsizeof(a_multi_step) / (1024 ** 3), "GB")
        print("Size of lambda_vector:", sys.getsizeof(lambda_vector) / (1024 ** 3), "GB")
        print("Size of mo :", sys.getsizeof(mo) / (1024 ** 3), "GB")

        del a

        time_start = time.time()

        # Simulation of steps
        for _ in range(num_simulations):
            mo = a_multi_step.dot(mo)

        print("Time taken simulating", num_simulations, "steps:", time.time() - time_start)

        """
        Step = 1
        Time taken creation of the TCPN solver: 11.625565767288208
        Size of pre : 0.00016239657998085022 GB
        Size of pi : 0.00020307675004005432 GB
        Size of c : 0.0003212280571460724 GB
        Size of a : 0.054637178778648376 GB
        Size of a multi-step: 0.054637178778648376 GB
        Size of lambda_vector: 0.00010162591934204102 GB
        Size of mo : 1.043081283569336e-07 GB
        Time taken simulating 2000 steps: 17.477917432785034
        
        Step = 0.75
        Simulation of execution with sparse and none sparse mix
        Size of pre and post (each one): 0.880668006837368 GB
        Density of pre: 0.00020682523267838676
        Density of post: 0.00021826335247145662
        Time taken creation of the model: 11.719517946243286
        Time taken creation of the TCPN solver: 62.1321918964386
        Size of pre : 0.00029123201966285706 GB
        Size of pi : 0.0003642924129962921 GB
        Size of c : 0.0005756020545959473 GB
        Size of a : 0.174174003303051 GB
        Size of a multi-step: 0.174174003303051 GB
        Size of lambda_vector: 0.0001822337508201599 GB
        Size of mo : 1.043081283569336e-07 GB
        Time taken simulating 2000 steps: 52.81004190444946
        
        Step = 0.65 (With swap)
        Simulation of execution with sparse and none sparse mix
        Size of pre and post (each one): 1.5406246408820152 GB
        Density of pre: 0.0001565680288085173
        Density of post: 0.00016527296940636537
        Time taken creation of the model: 49.70990824699402
        Time taken creation of the TCPN solver: 150.49850702285767
        Size of pre : 0.0003856159746646881 GB
        Size of pi : 0.00048242881894111633 GB
        Size of c : 0.0007623434066772461 GB
        Size of a : 0.3039373680949211 GB
        Size of a multi-step: 0.3039373680949211 GB
        Size of lambda_vector: 0.00024130195379257202 GB
        Size of mo : 1.043081283569336e-07 GB
        Time taken simulating 2000 steps: 93.01911354064941
        """


if __name__ == '__main__':
    unittest.main()
