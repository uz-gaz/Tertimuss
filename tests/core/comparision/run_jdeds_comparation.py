import csv
import json
import unittest
from random import randrange
from typing import List

import numpy

from main.core.execution_simulator.system_modeling.GlobalModel import GlobalModel
from main.core.execution_simulator.system_modeling.ThermalModelSelector import ThermalModelSelector
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult
from main.core.execution_simulator.system_simulator.SystemSimulator import SystemSimulator
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.automatic_task_generator.implementations.UUniFast import UUniFast
from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.implementations.RUN import RUNScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from main.plot_generator.implementations.ContextSwitchStatistics import ContextSwitchStatistics
from main.plot_generator.implementations.ExecutionPercentageStatistics import ExecutionPercentageStatistics


class RUNJDEDSComparisionTest(unittest.TestCase):
    def test_create_csv_from_comparision(self):
        results_to_print = []
        for i in range(10):
            name = "test_" + str(i)
            print(name)
            try:
                save_path = "out/experimentation/"
                simulation_name = name + "_"
                with open(save_path + simulation_name + "run_context_switch_statics.json", "r") as read_file:
                    decoded_json = json.load(read_file)
                    total_context_switch_number_run = decoded_json["statics"]["total_context_switch_number"]
                    scheduler_produced_context_switch_number_run = decoded_json["statics"][
                        "scheduler_produced_context_switch_number"]
                    mandatory_context_switch_number_run = decoded_json["statics"]["mandatory_context_switch_number"]
                    migrations_number_run = decoded_json["statics"]["migrations_number"]

                with open(save_path + simulation_name + "jdeds_context_switch_statics.json", "r") as read_file:
                    decoded_json = json.load(read_file)
                    total_context_switch_number_jdeds = decoded_json["statics"]["total_context_switch_number"]
                    scheduler_produced_context_switch_number_jdeds = decoded_json["statics"][
                        "scheduler_produced_context_switch_number"]
                    mandatory_context_switch_number_jdeds = decoded_json["statics"]["mandatory_context_switch_number"]
                    migrations_number_jdeds = decoded_json["statics"]["migrations_number"]

                results_to_print.append([name, total_context_switch_number_jdeds,
                                         scheduler_produced_context_switch_number_jdeds,
                                         mandatory_context_switch_number_jdeds, migrations_number_jdeds,
                                         total_context_switch_number_run, scheduler_produced_context_switch_number_run,
                                         mandatory_context_switch_number_run, migrations_number_run
                                         ])
            except Exception as e:
                print("Ha fallado")
                pass

        with open('out/experimentation/results.csv', 'w', newline='') as file:
            for j in results_to_print:
                writer = csv.writer(file)
                writer.writerow(j)

    def test_comparision(self):
        for i in range(10):
            name = "test_" + str(i)
            print(name)
            self.rec_comparision(name, 2)

    def test_one_comparision(self):
        name = "test_1"
        self.rec_comparision(name, 2, False)

    def rec_comparision(self, name: str, number_of_cpus: int, automatic_generation=True):
        save_path = "out/experimentation/"
        simulation_name = name + "_"
        x = []

        if automatic_generation:
            u = UUniFast()
            x = u.generate(
                {
                    "min_period_interval": 1,
                    "max_period_interval": 1,
                    "hyperperiod": 1,
                    "number_of_tasks": 4,
                    "utilization": number_of_cpus,
                    "processor_frequency": 100,
                }
            )

            for i in range(len(x)):
                multiplier = randrange(1, 9)
                x[i].d = x[i].d * multiplier
                x[i].t = x[i].t * multiplier
                x[i].c = x[i].c * multiplier * 10

            tasks_definition_dict = []

            for i in x:
                tasks_definition_dict.append({
                    "type": "Periodic",
                    "worst_case_execution_time": i.c,
                    "period": i.d
                })

            with open(save_path + simulation_name + "tasks_specification.json", 'w') as f:
                json.dump(tasks_definition_dict, f, indent=4)

        else:
            with open(save_path + simulation_name + "tasks_specification.json", "r") as read_file:
                decoded_json = json.load(read_file)
            for i in decoded_json:
                x.append(PeriodicTask(i["worst_case_execution_time"], i["period"], i["period"], 0))

        schedulers = [
            (RUNScheduler(), "run"),
            (AIECSScheduler(), "jdeds"),
        ]

        for scheduler_actual in schedulers:
            try:
                result, global_specification, simulation_kernel = self.create_problem_specification(x,
                                                                                                    scheduler_actual[0],
                                                                                                    number_of_cpus)
                result_save_path = scheduler_actual[1]

                if self._have_miss_deadline(global_specification, result):
                    print("Deadline perdido")
                    break
                else:
                    ExecutionPercentageStatistics.plot(global_specification, result,
                                                       {
                                                           "save_path": save_path + simulation_name + result_save_path +
                                                                        "_execution_percentage_statics.json"})

                    ContextSwitchStatistics.plot(global_specification, result,
                                                 {
                                                     "save_path": save_path + simulation_name
                                                                  + result_save_path + "_context_switch_statics.json"
                                                 })

            except Exception as e:
                print("Fail for " + scheduler_actual[1])
                print(e.args)
                break

    @staticmethod
    def _have_miss_deadline(global_specification: GlobalSpecification, scheduler_result: SchedulingResult) -> bool:
        """
             Plot task execution in each cpu
             :param global_specification: problem specification
             :param scheduler_result: result of scheduling
             """

        i_tau_disc = scheduler_result.scheduler_assignation
        frequencies = scheduler_result.frequencies

        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        n_periodic = len(global_specification.tasks_specification.periodic_tasks)
        n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

        frequencies_disc_f = numpy.concatenate(
            [numpy.repeat(i.reshape(1, -1), n_periodic + n_aperiodic, axis=0) for i in frequencies],
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

        i_tau_disc_accond = numpy.zeros((n_periodic + n_aperiodic, len(i_tau_disc[0])))

        for i in range(m):
            i_tau_disc_accond = i_tau_disc_accond + i_tau_disc[
                                                    i * (n_periodic + n_aperiodic): (i + 1) * (
                                                            n_periodic + n_aperiodic), :]
        number_deadline_missed = 0

        for i in range(n_periodic):
            missed_deadlines = 0
            missed_deadline_jobs = []
            missed_deadline_jobs_cycles = []
            period_ranges = list(range(0, hyperperiod, ti_p_dt[i]))
            for j in range(len(period_ranges)):
                if (sum(i_tau_disc_accond[i, period_ranges[j]: period_ranges[j] + di_p_dt[i]]) *
                    global_specification.simulation_specification.dt) / ci_p_dt[i] < 1.0:
                    missed_deadlines = missed_deadlines + 1
                    missed_deadline_jobs.append(j)
                    missed_deadline_jobs_cycles.append(
                        (sum(i_tau_disc_accond[i, period_ranges[j]: period_ranges[j] + di_p_dt[i]]) *
                         global_specification.simulation_specification.dt))

            if missed_deadlines > 0:
                number_deadline_missed = number_deadline_missed + missed_deadlines

        for i in range(n_aperiodic):
            if (sum(i_tau_disc_accond[n_periodic + i, ai_a_dt[i]: di_a_dt[i]]) *
                global_specification.simulation_specification.dt) / ci_a_dt[i] < 1.0:
                number_deadline_missed = number_deadline_missed + 1

        return number_deadline_missed != 0

    @staticmethod
    def create_problem_specification(tasks_set: List[PeriodicTask], scheduler: AbstractScheduler, number_of_cpus: int):

        tasks_specification: TasksSpecification = TasksSpecification(tasks_set)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150, 400, 600, 850, 1000],
                                                    number_of_cpus * [1000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01, False)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification,
                                                                        CpuSpecification(board_specification,
                                                                                         core_specification),
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification)

        return SystemSimulator.simulate(global_specification, global_model, scheduler,
                                        None), global_specification, global_model
