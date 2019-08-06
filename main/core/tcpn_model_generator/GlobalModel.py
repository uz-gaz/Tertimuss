import scipy

from main.core.tcpn_model_generator.ProcessorModel import ProcessorModel
from main.core.tcpn_model_generator.TasksModel import TasksModel
from main.core.tcpn_model_generator.ThermalModel import ThermalModel
from main.core.problem_specification.GlobalSpecification import GlobalSpecification


class GlobalModel(object):
    """
    Encapsulate all TCPN which represent the kernel of the simulation
    """

    def __init__(self, global_specification: GlobalSpecification):
        self.enable_thermal_mode = global_specification.simulation_specification.simulate_thermal

        n_periodic = len(global_specification.tasks_specification.periodic_tasks)

        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

        m = len(global_specification.cpu_specification.cores_specification.cores_frequencies)

        tasks_model: TasksModel = TasksModel(global_specification.tasks_specification,
                                             global_specification.cpu_specification)

        processor_model: ProcessorModel = ProcessorModel(global_specification.tasks_specification,
                                                         global_specification.cpu_specification)

        pre = scipy.block([
            [tasks_model.pre_tau, tasks_model.pre_alloc_tau,
             scipy.zeros((n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m))],
            [scipy.zeros((m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic)), processor_model.pre_alloc_proc,
             processor_model.pre_exec_proc]
        ])

        post = scipy.block([
            [tasks_model.post_tau, tasks_model.post_alloc_tau,
             scipy.zeros((n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m))],
            [scipy.zeros((m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic)), processor_model.post_alloc_proc,
             processor_model.post_exec_proc]
        ])

        pi = scipy.block([
            [tasks_model.pi_tau, tasks_model.pi_alloc_tau,
             scipy.zeros((n_periodic + n_periodic + n_aperiodic, (n_periodic + n_aperiodic) * m))],
            [scipy.zeros((m * (2 * (n_periodic + n_aperiodic) + 1), n_periodic)), processor_model.pi_alloc_proc,
             processor_model.pi_exec_proc]
        ]).transpose()

        lambda_vector = scipy.block([tasks_model.lambda_vector_tau, processor_model.lambda_vector_alloc_proc,
                                     processor_model.lambda_vector_exec_proc])

        mo = scipy.block([[tasks_model.mo_tau], [processor_model.mo_proc]])

        self.mo_proc_tau = mo
        self.pre_proc_tau = pre
        self.post_proc_tau = post
        self.pi_proc_tau = pi
        self.lambda_vector_proc_tau = lambda_vector

        if self.enable_thermal_mode:
            thermal_model: ThermalModel = global_specification.tcpn_model_specification.thermal_model_selector.value(
                global_specification.tasks_specification,
                global_specification.cpu_specification,
                global_specification.environment_specification,
                global_specification.simulation_specification)

            self.mo_thermal = thermal_model.mo_sis
            self.pre_thermal = thermal_model.pre_sis
            self.post_thermal = thermal_model.post_sis
            self.pi_thermal = thermal_model.pi_sis
            self.lambda_vector_thermal = thermal_model.lambda_vector_sis
            self.p_one_micro = thermal_model.p_one_micro
            self.p_board = thermal_model.p_board
            self.t_one_micro = thermal_model.t_one_micro
            self.t_board = thermal_model.t_board
            self.power_consumption = thermal_model.power_consumption
