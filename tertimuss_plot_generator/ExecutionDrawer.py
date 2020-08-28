from typing import Optional, Dict
import matplotlib.pyplot as plt

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class ExecutionDrawer(AbstractResultDrawer):

    @classmethod
    def plot(cls, global_specification: GlobalSpecification, scheduler_result: SchedulingResult,
             options: Dict[str, str]):
        """
        Plot results
        :param global_specification: Problem global specification
        :param scheduler_result: Result of the simulation
        :param options: Result drawer options

        Available options:
        save_path: path to save the simulation
        """
        cls.__plot_cpu_utilization(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_cpu_utilization(global_specification: GlobalSpecification, scheduler_result: SchedulingResult,
                               save_path: Optional[str] = None):
        """
        Plot cpu utilization
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """

        i_tau_disc = scheduler_result.scheduler_assignation
        time_u = scheduler_result.time_steps
        n_periodic = len(global_specification.tasks_specification.periodic_tasks)
        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)
        f, ax_arr = plt.subplots(nrows=m, num="CPU utilization", figsize=[14, 6])  # TODO: Add figsize as plot parameter

        for i in range(m):
            ax_arr[i].set_title("$CPU_" + str(i + 1) + "$ utilization")
            for j in range(n_periodic):
                ax_arr[i].plot(time_u, i_tau_disc[i * (n_periodic + n_aperiodic) + j],
                               label=r'$\tau_' + str(j + 1) + '$',
                               drawstyle='steps')
                ax_arr[i].set_xlabel('time (s)')
                ax_arr[i].axes.get_yaxis().set_visible(False)

            for j in range(n_aperiodic):
                ax_arr[i].plot(time_u, i_tau_disc[i * (n_periodic + n_aperiodic) + n_periodic + j],
                               label=r'$\tau_' + str(j + 1) + '^a$',
                               drawstyle='steps')
                ax_arr[i].axes.get_yaxis().set_visible(False)

            ax_arr[i].legend(loc='best')

        f.tight_layout()

        if save_path is None:
            plt.show()
        else:
            plt.savefig(save_path)

        plt.close(f)

        """
                fig, ax = plt.subplots()

        ax.broken_barh([(110, 30), (150, 10)], (10, 9), facecolors='tab:blue')

        ax.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9),
                       facecolors=('tab:orange', 'tab:green', 'tab:red'))
        ax.set_ylim(5, 35)
        ax.set_xlim(0, 200)
        ax.set_xlabel('seconds since start')
        ax.set_yticks([15, 25])
        ax.set_yticklabels(['Bill', 'Jim'])
        ax.grid(True)

        """
