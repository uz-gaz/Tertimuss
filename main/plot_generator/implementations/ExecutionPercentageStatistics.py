import json
from typing import Optional, Dict

import scipy

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult

from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class ExecutionPercentageStatistics(AbstractResultDrawer):

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
        cls.__plot_task_execution_percentage_statistics(global_specification, scheduler_result,
                                                        options.get("save_path"))

    @staticmethod
    def __plot_task_execution_percentage_statistics(global_specification: GlobalSpecification,
                                                    scheduler_result: SchedulingResult,
                                                    save_path: Optional[str] = None):
        """
        Plot task execution in each cpu
        :param global_specification: problem specification
        :param scheduler_result: result of scheduling
        :param save_path: path to save the simulation
        """

        i_tau_disc = scheduler_result.scheduler_assignation
        frequencies = scheduler_result.frequencies

        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        n_periodic = len(global_specification.tasks_specification.periodic_tasks)
        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

        frequencies_disc_f = scipy.concatenate(
            [scipy.repeat(i.reshape(1, -1), n_periodic + n_aperiodic, axis=0) for i in frequencies],
            axis=0)

        i_tau_disc = i_tau_disc * frequencies_disc_f

        hyperperiod = int(global_specification.tasks_specification.h / global_specification.simulation_specification.dt)

        ci_p_dt = [i.c for i in
                   global_specification.tasks_specification.periodic_tasks]

        di_p_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.periodic_tasks]

        ti_p_dt = [int(round(i.t / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.periodic_tasks]

        ci_a_dt = [i.c for i in
                   global_specification.tasks_specification.aperiodic_tasks]

        ai_a_dt = [int(round(i.a / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.aperiodic_tasks]

        di_a_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
                   global_specification.tasks_specification.aperiodic_tasks]

        i_tau_disc_accond = scipy.zeros((n_periodic + n_aperiodic, len(i_tau_disc[0])))

        for i in range(m):
            i_tau_disc_accond = i_tau_disc_accond + i_tau_disc[
                                                    i * (n_periodic + n_aperiodic): (i + 1) * (
                                                            n_periodic + n_aperiodic), :]

        deadline_missed_details = {}
        number_deadline_missed = 0

        for i in range(n_periodic):
            missed_deadlines = 0
            missed_deadline_jobs = []
            period_ranges = list(range(0, hyperperiod, ti_p_dt[i]))
            for j in range(len(period_ranges)):
                if (sum(i_tau_disc_accond[i, period_ranges[j]: period_ranges[j] + di_p_dt[i]]) *
                    global_specification.simulation_specification.dt) / ci_p_dt[i] < 1.0:
                    missed_deadlines = missed_deadlines + 1
                    missed_deadline_jobs.append(j)

            if missed_deadlines > 0:
                deadline_missed_details["task_" + str(i)] = {
                    "number_of_missed_deadlines": missed_deadlines,
                    "jobs_which_missed_deadlines": missed_deadline_jobs
                }
                number_deadline_missed = number_deadline_missed + missed_deadlines

        for i in range(n_aperiodic):
            if (sum(i_tau_disc_accond[n_periodic + i, ai_a_dt[i]: di_a_dt[i]]) *
                global_specification.simulation_specification.dt) / ci_a_dt[i] < 1.0:
                deadline_missed_details["aperiodic_" + str(i)] = {
                    "number_of_missed_deadlines": 1
                }
                number_deadline_missed = number_deadline_missed + 1

        json_to_return = {
            "statics": {
                "number_of_missed_deadlines": number_deadline_missed
            }
        }

        if deadline_missed_details:
            json_to_return["details"] = deadline_missed_details

        with open(save_path, 'w') as f:
            json.dump(json_to_return, f, indent=4)
