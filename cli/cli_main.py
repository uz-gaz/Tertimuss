import json
import os
import time
from typing import Optional
from jsonschema import validate, ValidationError

from cli.progress_bar_cli import ProgressBarCli
from core.kernel_generator.global_model import generate_global_model
from core.kernel_generator.kernel import SimulationKernel
from core.kernel_generator.processor_model import ProcessorModel, generate_processor_model
from core.kernel_generator.tasks_model import TasksModel, generate_tasks_model
from core.kernel_generator.thermal_model import ThermalModel, generate_thermal_model
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid, Origin, check_origins
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task
from core.schedulers.scheduler_selector_by_name import select_scheduler
from core.task_generator.task_generator_naming_selector import select_task_generator
from output_generation.abstract_progress_bar import AbstractProgressBar
from output_generation.output_generator import draw_heat_matrix, plot_task_execution, plot_cpu_utilization, \
    plot_cpu_temperature, \
    plot_accumulated_execution_time


def cli_main(args):
    # Progress bar
    if args.verbose:
        progress_bar: Optional[AbstractProgressBar] = ProgressBarCli()
    else:
        progress_bar: Optional[AbstractProgressBar] = None

    # Path of the input validate schema
    # Warning: In python paths are relative to the entry point script path
    input_schema_path = "./cli/input-schema/input-schema.json"

    # Read schema for validation
    if args.verbose:
        progress_bar.update("Data loading", 0)

    try:
        with open(input_schema_path, "r") as read_file:
            try:
                input_schema = json.load(read_file)
            except ValueError:
                print("Error: Wrong schema file syntax")
                return 1
    except IOError:
        print("Error: Can't read the schema", input_schema_path)
        return 1

    # Read input file
    try:
        with open(args.file, "r") as read_file:
            try:
                scenario_description = json.load(read_file)
            except ValueError:
                print("Error: Wrong input file syntax")
                return 1
    except IOError:
        print("Error: Can't read the file", args.file)
        return 1

    # Validate the input
    try:
        validate(scenario_description, input_schema)
    except ValidationError as ve:
        print("Error: Wrong fields validation in", '/'.join(map(lambda x: str(x), ve.absolute_path)), "with message",
              ve.message)
        return 1

    if args.verbose:
        progress_bar.update_progress(50)

    scenario_description = scenario_description.get("specification")

    if args.verbose:
        # Get previous time
        time_at_start = time.time()

    # True if is a specification with thermal
    is_specification_with_thermal = scenario_description.get("processor").get("boardProperties") is not None

    processor = scenario_description.get("processor")

    board_prop = processor.get("boardProperties") if is_specification_with_thermal else None
    board_physical_properties = board_prop.get("physicalProperties") if is_specification_with_thermal else None

    core_properties = processor.get("coresProperties")
    core_physical_properties = core_properties.get("physicalProperties") if is_specification_with_thermal else None

    cpu_origins = core_properties.get("coresOrigins") if is_specification_with_thermal else None

    # Check cpu origins spec
    if cpu_origins is not None:
        cpu_origins = list(map(lambda x: Origin(x.get("x"), x.get("y")), cpu_origins))

        if not check_origins(cpu_origins, core_physical_properties.get("shape").get("x"),
                             core_physical_properties.get("shape").get("y"),
                             board_physical_properties.get("shape").get("x"),
                             board_physical_properties.get("shape").get("y")) or len(
            cpu_origins) != core_properties.get("numberOfCores"):
            print("Error: Wrong cpu origins specification")
            return 1

    cpu_specification = CpuSpecification(
        MaterialCuboid(board_physical_properties.get("shape").get("x"),
                       board_physical_properties.get("shape").get("y"),
                       board_physical_properties.get("shape").get("z"),
                       board_physical_properties.get("density"),
                       board_physical_properties.get("specificHeatCapacity"),
                       board_physical_properties.get("thermalConductivity")
                       ) if is_specification_with_thermal else None,
        MaterialCuboid(core_physical_properties.get("shape").get("x"),
                       core_physical_properties.get("shape").get("y"),
                       core_physical_properties.get("shape").get("z"),
                       core_physical_properties.get("density"),
                       core_physical_properties.get("specificHeatCapacity"),
                       core_physical_properties.get("thermalConductivity")
                       ) if is_specification_with_thermal else None,
        core_properties.get("numberOfCores"),
        core_properties.get("frequencyScale"),
        cpu_origins)

    simulation_specification = SimulationSpecification(
        scenario_description.get("simulation").get("meshStepSize") if is_specification_with_thermal else None,
        scenario_description.get("simulation").get("timeStep"))

    environment_specification = EnvironmentSpecification(
        scenario_description.get("environment").get("convectionFactor"),
        scenario_description.get("environment").get("environmentTemperature"),
        scenario_description.get("environment").get("maximumTemperature")) if is_specification_with_thermal else None

    tasks = scenario_description.get("tasks")

    if type(tasks) is list:
        tasks_specification = TasksSpecification(list(
            map(lambda a: Task(a.get("worstCaseExecutionTime"), a.get("period"),
                               a.get("energyConsumption") if is_specification_with_thermal else None), tasks)))
    else:
        tasks_specification = select_task_generator(tasks.get("name"), tasks.get("numberOfTasks"),
                                                    tasks.get("utilizationOfTheTaskSet"), (
                                                        tasks.get("intervalForPeriods").get("min"),
                                                        tasks.get("intervalForPeriods").get("max")),
                                                    core_properties.get("frequencyScale"))
        if tasks_specification is None:
            print("Error: Wrong tasks specification")
            return 1
        else:
            tasks_specification = TasksSpecification(tasks_specification.generate())

    scheduler = select_scheduler(scenario_description.get("scheduler").get("name"), is_specification_with_thermal)

    if scheduler is None:
        print("Error: Wrong scheduler name")
        return 1

    # Run the simulation
    if args.verbose:
        progress_bar.update_progress(100)
        progress_bar.update("Kernel generation", 0)

    processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

    if args.verbose:
        progress_bar.update_progress(30)

    tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

    if args.verbose:
        progress_bar.update_progress(60)

    thermal_model: Optional[ThermalModel] = generate_thermal_model(tasks_specification, cpu_specification,
                                                                   environment_specification,
                                                                   simulation_specification) if is_specification_with_thermal else None

    global_model, mo = generate_global_model(tasks_model, processor_model, thermal_model, environment_specification)

    simulation_kernel: SimulationKernel = SimulationKernel(tasks_model, processor_model, thermal_model,
                                                           global_model, mo)

    global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                    environment_specification,
                                                                    simulation_specification)

    if args.verbose:
        progress_bar.update_progress(100)
        progress_bar.update("Scheduling", 0)

    try:
        simulation_result = scheduler.simulate(global_specification, simulation_kernel, progress_bar)
    except Exception as ex:
        print(ex)
        return 1

    if args.verbose:
        progress_bar.update_progress(100)
        progress_bar.close()

        # End simulation time
        time_at_end = time.time()
        print("Simulation time: ", time_at_end - time_at_start)

    output = scenario_description.get("output")

    output_path = output.get("path")
    output_base_name = output.get("baseName")

    # Create output directory if not exist
    os.makedirs(output_path, exist_ok=True)

    # Generate output files
    for i in output.get("generate"):
        if i == "allocationAndExecution":
            plot_cpu_utilization(global_specification, simulation_result,
                                 os.path.join(output_path, output_base_name + "_cpu_utilization.png"))
            plot_task_execution(global_specification, simulation_result,
                                os.path.join(output_path, output_base_name + "_task_execution.png"))
            plot_accumulated_execution_time(global_specification, simulation_result,
                                            os.path.join(output_path,
                                                         output_base_name + "_accumulated_execution_time.png"))
            if is_specification_with_thermal:
                plot_cpu_temperature(global_specification, simulation_result,
                                     os.path.join(output_path, output_base_name + "_cpu_temperature.png"))

        elif i == "temperatureEvolution":
            draw_heat_matrix(global_specification, simulation_kernel, simulation_result,
                             os.path.join(output_path, output_base_name + "heat_matrix.mp4"))
