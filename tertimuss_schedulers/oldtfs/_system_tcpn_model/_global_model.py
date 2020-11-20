from typing import Union

import numpy
import scipy.sparse

from ._processor_model import ProcessorModel
from ._tasks_model import TasksModel
from ._thermal_model import ThermalModel
from ._thermal_model_selector import ThermalModelSelector
from tertimuss_simulation_lib.system_definition import HomogeneousCpuSpecification, EnvironmentSpecification, TaskSet


class GlobalModel(object):
    """
    Encapsulate all TCPN which represent the global model of the simulation
    """

    def __init__(self, cpu_specification: Union[HomogeneousCpuSpecification],
                 environment_specification: EnvironmentSpecification,
                 task_set: TaskSet,
                 simulate_thermal=True,
                 simulation_precision=numpy.float64,
                 mesh_step: float = 0.01,
                 thermal_model_type: ThermalModelSelector = ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED):
        self.enable_thermal_mode = simulate_thermal

        n_periodic = len(task_set.periodic_tasks)

        n_aperiodic = len(task_set.aperiodic_tasks)

        m = cpu_specification.cores_specification.number_of_cores

        # Create tasks-processors model
        tasks_model: TasksModel = TasksModel(cpu_specification, task_set, simulation_precision)

        processor_model: ProcessorModel = ProcessorModel(cpu_specification, task_set, simulation_precision)

        pre = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pre_tau, tasks_model.pre_alloc_tau, scipy.sparse.csr_matrix(
                (n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m),
                dtype=simulation_precision)]),

            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic),
                dtype=simulation_precision),
                processor_model.pre_alloc_proc, processor_model.pre_exec_proc])
        ])

        post = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.post_tau, tasks_model.post_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m),
                                     dtype=simulation_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic),
                dtype=simulation_precision),
                processor_model.post_alloc_proc, processor_model.post_exec_proc])
        ])

        pi = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pi_tau, tasks_model.pi_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m),
                                     dtype=simulation_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic),
                dtype=simulation_precision),
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
            thermal_model: ThermalModel = thermal_model_type.value(cpu_specification, environment_specification,
                                                                   task_set, simulation_precision, mesh_step)

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
