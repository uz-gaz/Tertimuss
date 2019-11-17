import json
import unittest
from typing import List

from main.core.execution_simulator.system_modeling.GlobalModel import GlobalModel
from main.core.execution_simulator.system_modeling.ThermalModelSelector import ThermalModelSelector
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
from main.core.schedulers_definition.implementations.JDEDS import GlobalJDEDSScheduler
from main.core.schedulers_definition.implementations.RUN import RUNScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from main.plot_generator.implementations.ContextSwitchStatistics import ContextSwitchStatistics
from main.plot_generator.implementations.ExecutionPercentageStatistics import ExecutionPercentageStatistics
from main.plot_generator.implementations.UtilizationDrawer import UtilizationDrawer


class RUNJDEDSComparisionTest(unittest.TestCase):
    def test_comparision(self):
        for i in range(40):
            name = "test_" + str(i)
            print(name)
            self.rec_comparision(name)

    def rec_comparision(self, name):
        save_path = "out/experimentation/"
        simulation_name = name + "_"
        automatic_generation = True
        x = []

        if automatic_generation:
            u = UUniFast()
            x = u.generate(
                {
                    "min_period_interval": 2,
                    "max_period_interval": 10,
                    "hyperperiod": 10,
                    "number_of_tasks": 10,
                    "utilization": 2,
                    "processor_frequency": 10,
                }
            )

            x = [PeriodicTask(i.c * 100, i.t, i.d, i.e) for i in x]

            tasks_definition_dict = []

            for i in x:
                tasks_definition_dict.append({
                    "type": "Periodic",
                    "worst_case_execution_time": i.c,
                    "period": i.d
                })

            with open(save_path + simulation_name + "tasks_specification", 'w') as f:
                json.dump(tasks_definition_dict, f, indent=4)

        else:
            with open(save_path + simulation_name + "tasks_specification", "r") as read_file:
                decoded_json = json.load(read_file)
            for i in decoded_json:
                x.append(PeriodicTask(i["worst_case_execution_time"], i["period"], i["period"], 0))

        schedulers = [
            (GlobalJDEDSScheduler(), "jdeds"),
            (RUNScheduler(), "run"),
        ]

        # schedulers = [
        #     (RUNScheduler(), "run"),
        # ]

        for scheduler_actual in schedulers:
            try:
                result, global_specification, simulation_kernel = self.create_problem_specification(x,
                                                                                                    scheduler_actual[0])
                result_save_path = scheduler_actual[1]

                ExecutionPercentageStatistics.plot(global_specification, result,
                                                   {
                                                       "save_path": save_path + simulation_name + result_save_path +
                                                                    "_execution_percentage_statics.json"})

                ContextSwitchStatistics.plot(global_specification, result,
                                             {
                                                 "save_path": save_path + simulation_name
                                                              + result_save_path + "_context_switch_statics.json"
                                             })

                UtilizationDrawer.plot(global_specification, result,
                                       {"save_path": save_path + simulation_name
                                                     + result_save_path + "_cpu_utilization.png"})
            except Exception as e:
                print("Fail for " + scheduler_actual[1])
                print(e.args)

    @staticmethod
    def create_problem_specification(tasks_set: List[PeriodicTask], scheduler: AbstractScheduler):

        tasks_specification: TasksSpecification = TasksSpecification(tasks_set)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150, 400, 600, 850, 1000],
                                                    [1000, 1000])

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
