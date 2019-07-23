from typing import Optional, Dict

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
import matplotlib.pyplot as plt

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class AccumulatedExecutionTimeDrawer(AbstractResultDrawer):

    @classmethod
    def plot(cls, global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
             options: Dict[str, str]):
        """
        Plot results
        :param global_specification: Problem global specification
        :param scheduler_result: Result of the simulation
        :param options: Result drawer options

        Available options:
        save_path: path to save the simulation
        """
        cls.__plot_accumulated_execution_time(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_accumulated_execution_time(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                                        save_path: Optional[str] = None):
        """
        Plot tasks accumulated execution time during the simulation
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """

        mexec = scheduler_result.execution_time_scheduler
        # mexec_tcpn = scheduler_result.execution_time_tcpn
        time_u = scheduler_result.time_steps
        # time_step = scheduler_result.time_tcpn
        n_periodic = len(global_specification.tasks_specification.periodic_tasks)
        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)
        m = len(global_specification.cpu_specification.cores_specification.cores_frequencies)
        f, axarr = plt.subplots(nrows=m, ncols=(n_periodic + n_aperiodic), num="Execution time")
        for i in range(m):
            for j in range(n_periodic):
                axarr[i][j].set_title(r'$\tau_' + str(j + 1) + '$ execution \n on $CPU_' + str(i + 1) + '$')
                axarr[i][j].plot(time_u, mexec[i * (n_periodic + n_aperiodic) + j])
                # axarr[i][j].plot(time_step, mexec_tcpn[i * (n_periodic + n_aperiodic) + j], label="mexec tcpn")
                axarr[i][j].set_ylabel('executed time (s)')
                axarr[i][j].set_xlabel('system time (s)')

        for i in range(m):
            for j in range(n_aperiodic):
                axarr[i][j + n_periodic].set_title(
                    r'$\tau_' + str(j + 1) + '^a$ execution \n on $CPU_' + str(i + 1) + '$')
                axarr[i][j + n_periodic].plot(time_u, mexec[i * (n_periodic + n_aperiodic) + n_periodic + j])
                # axarr[i][j + n_periodic].plot(time_step, mexec_tcpn[i * (n_periodic + n_aperiodic) + n_periodic + j],
                #                               label="mexec tcpn")
                axarr[i][j + n_periodic].set_ylabel('executed time (s)')
                axarr[i][j + n_periodic].set_xlabel('system time (s)')

        f.tight_layout()

        if save_path is None:
            plt.show()
        else:
            plt.savefig(save_path)

        plt.close(f)
