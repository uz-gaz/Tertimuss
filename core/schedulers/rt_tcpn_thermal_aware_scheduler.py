import numpy as np

from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.processor_model import ProcessorModel
from core.kernel_generator.tasks_model import TasksModel
from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler
from core.schedulers.lineal_programing_problem_for_scheduling import solve_lineal_programing_problem_for_scheduling


class RTTcpnThermalAwareScheduler(AbstractScheduler):

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification, simulation_specification: SimulationSpecification,
                 global_model: GlobalModel, processor_model: ProcessorModel, tasks_model: TasksModel,
                 thermal_model: ThermalModel):
        jBi, jFSCi, quantum, mT = solve_lineal_programing_problem_for_scheduling(tasks_specification, cpu_specification,
                                                                                 environment_specification,
                                                                                 simulation_specification,
                                                                                 thermal_model)
        n = len(tasks_specification.tasks)
        m = cpu_specification.number_of_cores
        step = simulation_specification.dt

        ti = [i.t for i in tasks_specification.tasks]

        jobs = [int(i) for i in tasks_specification.h / ti]

        diagonal = np.zeros((n, np.max(jobs)))

        kd = 1
        sd = []
        for i in range(0, n):
            diagonal[i, 0: jobs[i]] = list(range(ti[i], ti[i], tasks_specification.h + 1))
            sd = np.union1d(sd, diagonal[i, 0: jobs[i]])

        sd = np.union1d(sd, [0])

        walloc = np.zeros(len(jFSCi))

        i_tau_disc = np.zeros((len(jFSCi), tasks_specification.h / quantum))
        e_iFSCj = np.zeros(len(walloc))
        x1 = np.zeros(len(e_iFSCj))  # ==np.zeros(walloc)
        x2 = np.zeros(len(e_iFSCj))
        s = np.zeros(len(e_iFSCj))
        iREj = np.zeros(len(walloc))
        iPRj = np.zeros((m, n))

        zeta = 0
        time = 0
        zeta_q = 1

        sd = sd[kd]

        m_exec = np.zeros(len(jFSCi))
        m_busy = np.zeros(len(jFSCi))
        Mexec = np.zeros(len(jFSCi))
        TIMEZ = []
        TIMEstep = []
        TIME_Temp = []
        TEMPERATURE_CONT = []
        TEMPERATURE_DISC = []
        MEXEC = []
        MEXEC_TCPN = []
        moDisc = global_model.mo
        M = []

        while round(zeta) <= tasks_specification.h:
            while round(time) <= zeta + quantum:
                for j in range(0, m):
                    for i in range(0, n):
                        # Calculo del error, y la superficie para el sliding mode control
                        e_iFSCj[i + j * n] = jFSCi[i + j * n] * zeta - m_exec[i + j * n]

        # TODO: Continue
