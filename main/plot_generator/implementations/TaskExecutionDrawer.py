from typing import Optional, Dict

import scipy

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
import matplotlib.pyplot as plt

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class TaskExecutionDrawer(AbstractResultDrawer):

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
        cls.__plot_task_execution(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_task_execution(global_specification: GlobalSpecification, scheduler_result: SchedulerResult,
                              save_path: Optional[str] = None):
        """
        Plot task execution in each cpu
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """

        i_tau_disc = scheduler_result.scheduler_assignation
        time_u = scheduler_result.time_steps
        n_periodic = len(global_specification.tasks_specification.periodic_tasks)
        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)
        m = len(global_specification.cpu_specification.cores_specification.cores_frequencies)
        f, axarr = plt.subplots(nrows=(n_periodic + n_aperiodic), num="Task execution")
        utilization_by_task = scipy.zeros(((n_periodic + n_aperiodic), len(i_tau_disc[0])))

        total_steps_number = int(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt)
        deadline_by_task = scipy.zeros(((n_periodic + n_aperiodic), total_steps_number))
        arrives_by_task = scipy.zeros((n_aperiodic, total_steps_number))
        deadlines_time = [i * global_specification.simulation_specification.dt for i in range(total_steps_number)]

        # Periodic tasks execution and deadlines
        for i in range(n_periodic):
            actual_deadline = int(
                global_specification.tasks_specification.periodic_tasks[
                    i].t / global_specification.simulation_specification.dt)
            for j in range(len(i_tau_disc[0])):
                for k in range(m):
                    utilization_by_task[i, j] += i_tau_disc[(n_periodic + n_aperiodic) * k + i, j]
            for j in range(total_steps_number):
                if j % actual_deadline == 0:
                    deadline_by_task[i][j] = 1

        # Aperiodic tasks execution and deadlines
        for i in range(n_aperiodic):
            deadline = int(
                global_specification.tasks_specification.aperiodic_tasks[
                    i].d / global_specification.simulation_specification.dt)
            arrive = int(
                global_specification.tasks_specification.aperiodic_tasks[
                    i].a / global_specification.simulation_specification.dt)
            for j in range(len(i_tau_disc[0])):
                for k in range(m):
                    utilization_by_task[i + n_periodic, j] += i_tau_disc[
                        (n_periodic + n_aperiodic) * k + n_periodic + i, j]

            deadline_by_task[n_periodic + i][deadline] = 1
            arrives_by_task[i][arrive] = 1

        for j in range(n_periodic):
            axarr[j].set_title(r'$\tau_' + str(j + 1) + '$ execution')
            axarr[j].plot(time_u, utilization_by_task[j], label="Execution", drawstyle='steps')
            axarr[j].plot(deadlines_time, deadline_by_task[j], label="Deadline", drawstyle='steps')
            axarr[j].legend(loc='best')
            axarr[j].set_xlabel('time (s)')
            axarr[j].axes.get_yaxis().set_visible(False)

        for j in range(n_aperiodic):
            axarr[j + n_periodic].set_title(r'$\tau_' + str(j + 1) + '^a$ execution')
            axarr[j + n_periodic].plot(time_u, utilization_by_task[n_periodic + j], label="Execution",
                                       drawstyle='steps')
            axarr[j + n_periodic].plot(deadlines_time, deadline_by_task[n_periodic + j], label="Deadline",
                                       drawstyle='steps')
            axarr[j + n_periodic].plot(deadlines_time, arrives_by_task[j], label="Arrive", drawstyle='steps')
            axarr[j + n_periodic].legend(loc='best')
            axarr[j + n_periodic].set_xlabel('time (s)')
            axarr[j + n_periodic].axes.get_yaxis().set_visible(False)

        f.tight_layout()

        if save_path is None:
            plt.show()
        else:
            plt.savefig(save_path)

        plt.close(f)
