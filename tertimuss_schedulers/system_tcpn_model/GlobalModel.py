import numpy
import scipy.sparse

from main.core.execution_simulator.system_modeling.ProcessorModel import ProcessorModel
from main.core.execution_simulator.system_modeling.TasksModel import TasksModel
from main.core.execution_simulator.system_modeling.ThermalModel import ThermalModel
from main.core.problem_specification.GlobalSpecification import GlobalSpecification


class GlobalModel(object):
    """
    Encapsulate all TCPN which represent the global model of the simulation
    """

    def __init__(self, global_specification: GlobalSpecification):
        self.enable_thermal_mode = global_specification.simulation_specification.simulate_thermal

        n_periodic = len(global_specification.tasks_specification.periodic_tasks)

        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        # Create tasks-processors model
        tasks_model: TasksModel = TasksModel(global_specification.tasks_specification,
                                             global_specification.cpu_specification,
                                             global_specification.simulation_specification)

        processor_model: ProcessorModel = ProcessorModel(global_specification.tasks_specification,
                                                         global_specification.cpu_specification,
                                                         global_specification.simulation_specification)

        pre = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pre_tau, tasks_model.pre_alloc_tau, scipy.sparse.csr_matrix(
                (n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m),
                dtype=global_specification.simulation_specification.type_precision)]),

            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic),
                dtype=global_specification.simulation_specification.type_precision),
                processor_model.pre_alloc_proc, processor_model.pre_exec_proc])
        ])

        post = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.post_tau, tasks_model.post_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m),
                                     dtype=global_specification.simulation_specification.type_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic),
                dtype=global_specification.simulation_specification.type_precision),
                processor_model.post_alloc_proc, processor_model.post_exec_proc])
        ])

        pi = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pi_tau, tasks_model.pi_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m),
                                     dtype=global_specification.simulation_specification.type_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic),
                dtype=global_specification.simulation_specification.type_precision),
                processor_model.pi_alloc_proc,
                processor_model.pi_exec_proc])
        ]).transpose()

        lambda_vector = numpy.block([tasks_model.lambda_vector_tau, processor_model.lambda_vector_alloc_proc,
                                     processor_model.lambda_vector_exec_proc])

        mo = numpy.block([[tasks_model.mo_tau], [processor_model.mo_proc]])

        self.mo_proc_tau: numpy.ndarray = mo
        self.pre_proc_tau: scipy.sparse.csr_matrix = pre
        self.post_proc_tau: scipy.sparse.csr_matrix = post
        self.pi_proc_tau: scipy.sparse.csr_matrix = pi
        self.lambda_vector_proc_tau: numpy.ndarray = lambda_vector

        # Create thermal model
        if self.enable_thermal_mode:
            thermal_model: ThermalModel = global_specification.tcpn_model_specification.thermal_model_selector.value(
                global_specification.tasks_specification,
                global_specification.cpu_specification,
                global_specification.environment_specification,
                global_specification.simulation_specification)

            self.mo_thermal: numpy.ndarray = thermal_model.mo_sis
            self.pre_thermal: scipy.sparse.csr_matrix = thermal_model.pre_sis
            self.post_thermal: scipy.sparse.csr_matrix = thermal_model.post_sis
            self.pi_thermal: scipy.sparse.csr_matrix = thermal_model.pi_sis
            self.lambda_vector_thermal: numpy.ndarray = thermal_model.lambda_vector_sis
            self.p_one_micro: int = thermal_model.p_one_micro
            self.p_board: int = thermal_model.p_board
            self.t_one_micro: int = thermal_model.t_one_micro
            self.t_board: int = thermal_model.t_board
            self.power_consumption: numpy.ndarray = thermal_model.power_consumption
