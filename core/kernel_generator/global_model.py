from scipy import linalg
import scipy

from core.kernel_generator.processor_model import ProcessorModel
from core.kernel_generator.tasks_model import TasksModel
from core.problem_specification_models.CpuSpecification import CpuSpecification

from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class GlobalModel(object):
    """
    Encapsulate all TCPN which represent the kernel of the simulation
    """

    def __init__(self, global_specification: GlobalSpecification):
        tasks_model: TasksModel = TasksModel(global_specification.tasks_specification,
                                             global_specification.cpu_specification)
        a_tau = (tasks_model.c_tau.dot(tasks_model.lambda_tau)).dot(tasks_model.pi_tau)

        processor_model: ProcessorModel = ProcessorModel(global_specification.tasks_specification,
                                                         global_specification.cpu_specification)
        a_proc = (processor_model.c_proc.dot(processor_model.lambda_proc)).dot(processor_model.pi_proc)

        # thermal_model: ThermalModel = generate_thermal_model(global_specification.tasks_specification,
        #                                                     global_specification.cpu_specification,
        #                                                     global_specification.environment_specification,
        #                                                     global_specification.simulation_specification)

        # if thermal_model is not None:
        #   return generate_global_model_with_thermal(tasks_model, processor_model, thermal_model,
        #                                             environment_specification)
        if True:
            a = linalg.block_diag(a_tau, a_proc)

            b = scipy.concatenate((tasks_model.c_tau_alloc, processor_model.c_proc_alloc,))

            bp = scipy.concatenate((scipy.zeros((len(a_tau), 1)), scipy.zeros((len(processor_model.c_proc_alloc), 1))))

            s = scipy.concatenate((processor_model.s_busy, processor_model.s_exec))
            s = linalg.block_diag(s)
            s = scipy.concatenate((scipy.zeros((len(s), len(a_tau))), s), axis=1)

            s_thermal = scipy.asarray([])

            mo = scipy.concatenate((tasks_model.m_tau_o, processor_model.m_proc_o))

        """
        Save copy of processor, task and thermal models
        """
        self.__task_model = tasks_model
        self.__processor_model = processor_model
        # self.__thermal_model = thermal_model

        """
        Create a global model
        """
        self.a = a
        self.b = b
        self.bp = bp
        self.s = s
        self.s_thermal = s_thermal
        self.m = mo  # Save marking in global model

    def change_frequency(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):
        # TODO: TEST, only done processor change frequency
        self.__processor_model.change_frequency(tasks_specification, cpu_specification)
        a_proc = (self.__processor_model.c_proc.dot(self.__processor_model.lambda_proc)).dot(
            self.__processor_model.pi_proc)
        self.a[self.a.shape[0] - a_proc.shape[0]:self.a.shape[0],
        self.a.shape[1] - a_proc.shape[1]:self.a.shape[1]] = a_proc

    """
    @staticmethod
    def generate_with_thermal(tasks_model: TasksModel, processor_model: ProcessorModel,
                              thermal_model: ThermalModel, environment_specification: EnvironmentSpecification) \
            -> [GlobalModel, scipy.ndarray]:
        a = linalg.block_diag(tasks_model.a_tau, processor_model.a_proc, thermal_model.a_t)

        b = scipy.concatenate((tasks_model.c_tau_alloc, processor_model.c_proc_alloc, thermal_model.ct_exec))

        bp = scipy.concatenate(
            (scipy.zeros((len(tasks_model.a_tau), 1)), scipy.zeros((len(processor_model.c_proc_alloc), 1)),
             thermal_model.b_ta.reshape((len(thermal_model.b_ta), 1))))

        s = scipy.concatenate((processor_model.s_busy, processor_model.s_exec))
        s = linalg.block_diag(s, thermal_model.s_t)
        s = scipy.concatenate((scipy.zeros((len(s), len(tasks_model.a_tau))), s), axis=1)

        s_thermal = scipy.zeros((len(thermal_model.a_t), len(tasks_model.a_tau) + len(processor_model.a_proc)))
        s_thermal = scipy.concatenate((s_thermal, scipy.identity(len(thermal_model.a_t))), axis=1)

        mo = scipy.full((len(thermal_model.a_t), 1), environment_specification.t_env)
        mo = scipy.concatenate((tasks_model.m_tau_o, processor_model.m_proc_o, mo))

        return GlobalModel(a, b, bp, s, s_thermal), mo
    """
