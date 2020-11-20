import argparse
import json
import os
import random
from multiprocessing.pool import Pool
from typing import List, Tuple

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
from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.Task import Task
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.implementations.RUN import RUNScheduler
from main.core.schedulers_definition.implementations.RUNA import RUNAScheduler
from main.core.schedulers_definition.implementations.SemiPartitionedAIECS import SemiPartitionedAIECSScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from main.plot_generator.implementations.ContextSwitchStatistics import ContextSwitchStatistics
from main.plot_generator.implementations.ExecutionPercentageStatistics import ExecutionPercentageStatistics
from main.plot_generator.implementations.TaskExecutionDrawer import TaskExecutionDrawer
from main.plot_generator.implementations.UtilizationDrawer import UtilizationDrawer


def worker_function(local_work_to_do: Tuple[int, int, str]):
    number_of_cpus = local_work_to_do[0]
    number_of_tasks = local_work_to_do[1]
    save_path = local_work_to_do[2]

    name = save_path
    print(str(number_of_cpus) + "/" + str(number_of_tasks) + "/" + name)
    run_comparison_from_saved_task_set(save_path, number_of_cpus, number_of_tasks)


def create_save_dir(processor_task_configurations: List[Tuple[int, int]]):
    for processor_task_configuration in processor_task_configurations:
        number_of_cpus = processor_task_configuration[0]
        number_of_tasks = processor_task_configuration[1]

        save_path = "out/" + str(number_of_cpus) + "/" + str(number_of_tasks) + "/"

        # Create dir if not exist
        if not os.path.exists(save_path):
            os.makedirs(save_path)


def run_comparison_from_saved_task_set(experiment_name: str, number_of_cpus: int, number_of_tasks: int) -> bool:
    simulation_name = experiment_name + "_"

    x = []
    with open(simulation_name + "tasks_specification.json", "r") as read_file:
        decoded_json = json.load(read_file)
    for i in decoded_json:
        x.append(PeriodicTask(i["worst_case_execution_time"], i["period"], i["period"], 0))

    schedulers = [
        (SemiPartitionedAIECSScheduler(), "semipartitionedaiecs")
        # (RUNScheduler(), "run"),
        # ,
        # (AIECSScheduler(), "aiecs")
    ]

    task_set_scheduled_by_all_schedulers: bool = True

    for scheduler_actual in schedulers:
        try:
            result, global_specification, simulation_kernel = create_problem_specification(x,
                                                                                           scheduler_actual[0],
                                                                                           number_of_cpus)
            result_save_path = scheduler_actual[1]

            if _have_miss_deadline(global_specification, result):
                print("Deadline perdido")
                break
            # else:
            ExecutionPercentageStatistics.plot(global_specification, result,
                                               {
                                                   "save_path": simulation_name + result_save_path +
                                                                "_execution_percentage_statics.json"})

            ContextSwitchStatistics.plot(global_specification, result,
                                         {
                                             "save_path": simulation_name
                                                          + result_save_path + "_context_switch_statics.json"
                                         })

        except Exception as e:
            print("Fail for " + scheduler_actual[1])
            print(e.args)
            task_set_scheduled_by_all_schedulers = False
            break

    return task_set_scheduled_by_all_schedulers


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
        [numpy.repeat(i.reshape(1, -1), n_periodic + n_aperiodic, axis=0) for i in frequencies], axis=0)

    i_tau_disc = i_tau_disc * frequencies_disc_f

    hyperperiod = int(global_specification.tasks_specification.convection_factor / global_specification.simulation_specification.dt)

    ci_p_dt = [i.c for i in
               global_specification.tasks_specification.periodic_tasks]

    di_p_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.periodic_tasks]

    ti_p_dt = [int(round(i.temperature / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.periodic_tasks]

    ci_a_dt = [i.c for i in global_specification.tasks_specification.aperiodic_tasks]

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


def create_problem_specification(tasks_set: List[Task], scheduler: AbstractScheduler, number_of_cpus: int):
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


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Configure comparative scenario')
    # parser.add_argument("-s", "--start_iteration", help="first iteration", required=True)
    # parser.add_argument("-cs", "--iterations_chunk_size", help="size of work chunk", required=True)
    # parser.add_argument("-n", "--number_of_iterations_chunks", help="number of work chunks", required=True)
    # parser.add_argument("-j", "--parallel_level", help="level of parallelization", required=True)
    # arguments = parser.parse_args()

    # Create dir to save
    # iterations_chunk_size = int(arguments.iterations_chunk_size)
    # global_start_iteration = int(arguments.start_iteration)
    # number_of_iterations_chunks = int(arguments.number_of_iterations_chunks)
    number_of_threads = 4

    work_to_do: List[Tuple[int, int, str]] = []

    base_folder = "JDEDS_4_24/"

    for i in range(220):
        experiment_file_name = base_folder + "test_" + str(i)
        if os.path.isfile("./" + experiment_file_name + "_tasks_specification.json") and \
                os.path.isfile("./" + experiment_file_name + "_aiecs_context_switch_statics.json") and \
                os.path.isfile("./" + experiment_file_name + "_run_context_switch_statics.json"):
            work_to_do.append((4, 24, experiment_file_name))

    # Create work packages
    p = Pool(processes=number_of_threads)
    p.map(worker_function, work_to_do)

    p.close()
    p.join()
