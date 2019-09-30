import json
from typing import Optional, Dict

import scipy

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class ContextSwitchStatistics(AbstractResultDrawer):

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
        cls.__plot_context_switch_statistics(global_specification, scheduler_result, options.get("save_path"))

    @staticmethod
    def __plot_context_switch_statistics(global_specification: GlobalSpecification, scheduler_result: SchedulingResult,
                                         save_path: Optional[str] = None):
        """
        Plot task execution in each cpu
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """

        i_tau_disc = scheduler_result.scheduler_assignation
        n_periodic = len(global_specification.tasks_specification.periodic_tasks)
        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        last_executed_cpu = -1 * scipy.ones(n_periodic + n_aperiodic)
        last_cycle_execution = -1 * scipy.ones(n_periodic + n_aperiodic)

        context_changes_by_tasks = scipy.zeros(n_periodic + n_aperiodic)
        migrations_changes_by_tasks = scipy.zeros(n_periodic + n_aperiodic)

        for i in range(len(i_tau_disc[0])):
            for j in range(n_periodic):
                actual_deadline = int(
                    global_specification.tasks_specification.periodic_tasks[
                        j].t / global_specification.simulation_specification.dt)
                if i % actual_deadline == 0:
                    last_executed_cpu[j] = -1
                    last_cycle_execution[j] = -1

            actual_step = i_tau_disc[:, i]

            for task_no in range(n_aperiodic + n_periodic):
                # Get the cpu where the task is being executed
                possible_cpu = [actual_cpu for actual_cpu in range(m) if
                                actual_step[task_no + (n_aperiodic + n_periodic) * actual_cpu] == 1]
                actual_execution_cpu = -1 if len(possible_cpu) == 0 else possible_cpu[0]

                if last_cycle_execution[task_no] != actual_execution_cpu and last_cycle_execution[task_no] != -1:
                    # Context change
                    context_changes_by_tasks[task_no] = context_changes_by_tasks[task_no] + 1

                if last_executed_cpu[task_no] != actual_execution_cpu and last_executed_cpu[
                    task_no] != -1 and actual_execution_cpu != -1:
                    # Migration
                    migrations_changes_by_tasks[task_no] = migrations_changes_by_tasks[task_no] + 1

                last_cycle_execution[task_no] = actual_execution_cpu

                if actual_execution_cpu != -1:
                    last_executed_cpu[task_no] = actual_execution_cpu

        jobs_by_tasks = [int(
            global_specification.tasks_specification.h / global_specification.tasks_specification.periodic_tasks[i].d)
                            for i in range(n_periodic)] + n_aperiodic * [1]

        # Is assumed that each job was executed
        output_statics = {
            "statics": {
                "total_context_switch_number": int(sum(context_changes_by_tasks)),
                "scheduler_produced_context_switch_number": int(sum(
                    [context_changes_by_tasks[i] - jobs_by_tasks[i] for i in range(n_periodic + n_aperiodic)])),
                "mandatory_context_switch_number": int(sum(
                    [jobs_by_tasks[i] for i in range(n_periodic + n_aperiodic)])),
                "migrations_number": int(sum(migrations_changes_by_tasks))
            },
            "details": [{
                "task_" + str(task_no): {
                    "total_context_switch_number": int(context_changes_by_tasks[task_no]),
                    "mandatory_context_switch_number": int(context_changes_by_tasks[task_no] - jobs_by_tasks[task_no]),
                    "scheduler_produced_context_switch_number": int(jobs_by_tasks[task_no]),
                    "migrations_number": int(migrations_changes_by_tasks[task_no])
                }
            } for task_no in range(n_periodic)] + [
                           {
                               "aperiodic_" + str(task_no): {
                                   "total_context_switch_number": int(context_changes_by_tasks[n_periodic + task_no]),
                                   "scheduler_produced_context_switch_number": int(
                                       context_changes_by_tasks[n_periodic + task_no] -
                                       jobs_by_tasks[n_periodic + task_no]),
                                   "mandatory_context_switch_number": int(jobs_by_tasks[n_periodic + task_no]),
                                   "migrations_number": int(migrations_changes_by_tasks[n_periodic + task_no])
                               }
                           } for task_no in range(n_aperiodic)]
        }
        with open(save_path, 'w') as f:
            json.dump(output_statics, f, indent=4)
