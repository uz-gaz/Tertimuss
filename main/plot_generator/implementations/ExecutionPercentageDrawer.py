from typing import Optional, Dict

import scipy

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
import matplotlib.pyplot as plt

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class ExecutionPercentageDrawer(AbstractResultDrawer):

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
        cls.__plot_task_execution_percentage(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_task_execution_percentage(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                                       save_path: Optional[str] = None):
        """
        Plot task execution in each cpu
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """

        i_tau_disc = scheduler_result.scheduler_assignation
        frequencies = scheduler_result.frequencies

        n_periodic = len(global_specification.tasks_specification.periodic_tasks)
        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

        frequencies_disc_f = scipy.concatenate(
            [scipy.repeat(i.reshape(1, -1), n_periodic + n_aperiodic, axis=0) for i in frequencies],
            axis=0)

        i_tau_disc = i_tau_disc * frequencies_disc_f

        hyperperiod = int(global_specification.tasks_specification.h / global_specification.simulation_specification.dt)

        ai = [int(global_specification.tasks_specification.h / i.t) for i in
              global_specification.tasks_specification.periodic_tasks]

        task_percentage_periodic = [scipy.zeros(i) for i in ai]

        task_percentage_aperiodic = []

        ci_p_dt = [int(round(i.c / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.periodic_tasks]

        di_p_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.periodic_tasks]

        ti_p_dt = [int(round(i.t / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.periodic_tasks]

        ci_a_dt = [int(round(i.c / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.aperiodic_tasks]

        ai_a_dt = [int(round(i.a / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.aperiodic_tasks]

        di_a_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.aperiodic_tasks]

        i_tau_disc_accond = scipy.zeros((n_periodic + n_aperiodic, len(i_tau_disc[0])))

        for i in range(global_specification.cpu_specification.number_of_cores):
            i_tau_disc_accond = i_tau_disc_accond + i_tau_disc[
                                                    i * (n_periodic + n_aperiodic): (i + 1) * (
                                                            n_periodic + n_aperiodic), :]

        for i in range(n_periodic):
            period_ranges = range(0, hyperperiod, ti_p_dt[i])
            task_percentage_periodic[i][:] = [sum(i_tau_disc_accond[i, j: j + di_p_dt[i]]) / ci_p_dt[i] for j in
                                              period_ranges]

        for i in range(n_aperiodic):
            execution_aperiodic = sum(i_tau_disc_accond[n_periodic + i, ai_a_dt[i]: di_a_dt[i]]) / ci_a_dt[i]
            task_percentage_aperiodic.append([execution_aperiodic])

        f, axarr = plt.subplots(nrows=(n_periodic + n_aperiodic), num="Task execution")

        for j in range(n_periodic):
            axarr[j].set_title(r'$\tau_' + str(j + 1) + '$ execution percentage in each period')
            to_draw = task_percentage_periodic[j]
            axarr[j].bar(list(range(len(to_draw))), to_draw,
                         align='center')
            axarr[j].set_ylabel('executed\n percentage')
            axarr[j].set_xlabel('periods / execution percentage')
            axarr[j].set_xticks(list(range(len(to_draw))))
            axarr[j].set_xticklabels([str(round(i * 100, 2)) + "%" for i in to_draw])

        for j in range(n_aperiodic):
            axarr[n_periodic + j].set_title(r'$\tau_' + str(j + 1) + '^a$ execution percentage')
            axarr[n_periodic + j].bar([1], task_percentage_aperiodic[j],
                                      align='center')
            axarr[n_periodic + j].set_xticklabels([])
            axarr[n_periodic + j].set_ylabel('executed\n percentage')
            axarr[n_periodic + j].set_xlabel('periods')

        f.tight_layout()

        if save_path is None:
            plt.show()
        else:
            plt.savefig(save_path)

        plt.close(f)
