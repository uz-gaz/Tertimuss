from typing import Dict, List, Tuple

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


class JSONGlobalModelParser(object):
    @staticmethod
    def read_input(input_path) -> [Dict]:
        # TODO
        pass

        # try:
        #     with open(input_schema_path, "r") as read_file:
        #         try:
        #             input_schema = json.load(read_file)
        #         except ValueError:
        #             print("Error: Wrong schema file syntax")
        #             return 1
        # except IOError:
        #     print("Error: Can't read the schema", input_schema_path)
        #     return 1

    @staticmethod
    def validate_input(input_json: Dict, schema_json: Dict) -> [bool, str]:
        # TODO
        pass

        # Validate the input
        # TODO: Fix to allow reference in input
        # try:
        #     validate(scenario_description, input_schema)
        # except ValidationError as ve:
        #     print("Error: Wrong fields validation in", '/'.join(map(lambda x: str(x), ve.absolute_path)), "with message",
        #           ve.message)
        #     return 1

    @staticmethod
    def obtain_global_model(input_json: Dict) -> [GlobalSpecification, AbstractScheduler,
                                                  List[Tuple[AbstractResultDrawer, Dict[str, str]]], Dict]:
        # TODO
        pass
        #
        # # TODO:
        # # True if is a specification with thermal
        # is_specification_with_thermal = scenario_description.get("processor").get("boardProperties") is not None
        #
        # processor = scenario_description.get("processor")
        #
        # board_prop = processor.get("boardProperties") if is_specification_with_thermal else None
        # board_physical_properties = board_prop.get("physicalProperties") if is_specification_with_thermal else None
        #
        # core_properties = processor.get("coresProperties")
        # core_physical_properties = core_properties.get("physicalProperties") if is_specification_with_thermal else None
        #
        # cpu_origins = core_properties.get("coresOrigins") if is_specification_with_thermal else None
        #
        # # Check cpu origins spec
        # if cpu_origins is not None:
        #     cpu_origins = list(map(lambda x: Origin(x.get("x"), x.get("y")), cpu_origins))
        #
        #     if not check_origins(cpu_origins, core_physical_properties.get("shape").get("x"),
        #                          core_physical_properties.get("shape").get("y"),
        #                          board_physical_properties.get("shape").get("x"),
        #                          board_physical_properties.get("shape").get("y")) or len(
        #         cpu_origins) != core_properties.get("numberOfCores"):
        #         print("Error: Wrong cpu origins specification")
        #         return 1
        #
        # cpu_specification = CpuSpecification(
        #     MaterialCuboid(board_physical_properties.get("shape").get("x"),
        #                    board_physical_properties.get("shape").get("y"),
        #                    board_physical_properties.get("shape").get("z"),
        #                    board_physical_properties.get("density"),
        #                    board_physical_properties.get("specificHeatCapacity"),
        #                    board_physical_properties.get("thermalConductivity")
        #                    ) if is_specification_with_thermal else None,
        #     MaterialCuboid(core_physical_properties.get("shape").get("x"),
        #                    core_physical_properties.get("shape").get("y"),
        #                    core_physical_properties.get("shape").get("z"),
        #                    core_physical_properties.get("density"),
        #                    core_physical_properties.get("specificHeatCapacity"),
        #                    core_physical_properties.get("thermalConductivity")
        #                    ) if is_specification_with_thermal else None,
        #     core_properties.get("numberOfCores"),
        #     core_properties.get("frequencyScale"),
        #     cpu_origins)
        #
        # simulation_specification = SimulationSpecification(
        #     scenario_description.get("simulation").get("meshStepSize") if is_specification_with_thermal else None,
        #     scenario_description.get("simulation").get("timeStep"))
        #
        # environment_specification = EnvironmentSpecification(
        #     scenario_description.get("environment").get("convectionFactor"),
        #     scenario_description.get("environment").get("environmentTemperature"),
        #     scenario_description.get("environment").get(
        #         "maximumTemperature")) if is_specification_with_thermal else None
        #
        # tasks = scenario_description.get("tasks")
        #
        # if type(tasks) is list:
        #     tasks_specification = TasksSpecification(list(
        #         map(lambda a: PeriodicTask(a.get("worstCaseExecutionTime"), a.get("period"),
        #                                    a.get("energyConsumption") if is_specification_with_thermal else None),
        #             tasks)))
        # else:
        #     tasks_specification = select_task_generator(tasks.get("name"), tasks.get("numberOfTasks"),
        #                                                 tasks.get("utilizationOfTheTaskSet"), (
        #                                                     tasks.get("intervalForPeriods").get("min"),
        #                                                     tasks.get("intervalForPeriods").get("max")),
        #                                                 core_properties.get("frequencyScale"))
        #     if tasks_specification is None:
        #         print("Error: Wrong tasks specification")
        #         return 1
        #     else:
        #         tasks_specification = TasksSpecification(tasks_specification.generate())
        #
        # scheduler = select_scheduler(scenario_description.get("scheduler").get("name"), is_specification_with_thermal)
        #
        # if scheduler is None:
        #     print("Error: Wrong scheduler name")
        #     return 1
        #
        # # Run the simulation
        # if args.verbose:
        #     progress_bar.update_progress(100)
        #     progress_bar.update("Kernel generation", 0)
        #
        # processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)
        #
        # if args.verbose:
        #     progress_bar.update_progress(30)
        #
        # tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)
        #
        # if args.verbose:
        #     progress_bar.update_progress(60)
        #
        # thermal_model: Optional[ThermalModel] = generate_thermal_model(tasks_specification, cpu_specification,
        #                                                                environment_specification,
        #                                                                simulation_specification) if is_specification_with_thermal else None
        #
        # global_model, mo = generate_global_model(tasks_model, processor_model, thermal_model, environment_specification)
        #
        # simulation_kernel: SimulationKernel = SimulationKernel(tasks_model, processor_model, thermal_model,
        #                                                        global_model, mo)
        #
        # global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
        #                                                                 environment_specification,
        #                                                                 simulation_specification)
