import argparse
import json
import os

from jsonschema import validate, ValidationError

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
from core.schedulers.scheduler_naming_selector import select_scheduler
from core.task_generator.task_generator_naming_selector import select_task_generator
from gui.output_generator import draw_heat_matrix, plot_task_execution, plot_cpu_utilization, plot_cpu_temperature, \
    plot_accumulated_execution_time


def main(args):
    # Path of the input validate schema
    input_schema_path = "input-schema-thermal-v1.0.json"

    # Read schema for validation
    try:
        with open(input_schema_path, "r") as read_file:
            try:
                input_schema = json.load(read_file)
            except ValueError:
                print("Error: Wrong schema file syntax")
                return 1
    except IOError:
        print("Error: Can't read the schema ", args.file)
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
        print("Error: Can't read the file ", args.file)
        return 1

    # Validate the input
    try:
        validate(scenario_description, input_schema)
    except ValidationError as ve:
        print("Error: Wrong fields validation in", '/'.join(map(lambda x: str(x), ve.absolute_path)), "with message",
              ve.message)
        return 1

    # TODO: Add no thermal
    scenario_description = scenario_description.get("specification")

    processor = scenario_description.get("processor")

    board_prop = processor.get("boardProperties")
    board_physical_properties = board_prop.get("physicalProperties")

    core_properties = processor.get("coresProperties")
    core_physical_properties = core_properties.get("physicalProperties")

    cpu_origins = core_properties.get("coresOrigins")

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
                       ),
        MaterialCuboid(core_physical_properties.get("shape").get("x"),
                       core_physical_properties.get("shape").get("y"),
                       core_physical_properties.get("shape").get("z"),
                       core_physical_properties.get("density"),
                       core_physical_properties.get("specificHeatCapacity"),
                       core_physical_properties.get("thermalConductivity")),
        core_properties.get("numberOfCores"),
        core_properties.get("frequencyScale"),
        cpu_origins)

    simulation_specification = SimulationSpecification(scenario_description.get("simulation").get("meshStepSize"),
                                                       scenario_description.get("simulation").get("timeStep"))

    environment_specification = EnvironmentSpecification(
        scenario_description.get("environment").get("convectionFactor"),
        scenario_description.get("environment").get("environmentTemperature"),
        scenario_description.get("environment").get("maximumTemperature"))

    tasks = scenario_description.get("tasks")

    if type(tasks) is list:
        tasks_specification = TasksSpecification(list(
            map(lambda a: Task(a.get("worstCaseExecutionTime"), a.get("period"), a.get("energyConsumption")), tasks)))
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

    scheduler = select_scheduler(scenario_description.get("scheduler").get("name"))

    if scheduler is None:
        print("Error: Wrong scheduler specification")
        return 1

    # Run the simulation
    processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

    tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

    thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                         environment_specification,
                                                         simulation_specification)

    global_model, mo = generate_global_model(tasks_model, processor_model, thermal_model, environment_specification)

    simulation_kernel: SimulationKernel = SimulationKernel(tasks_model, processor_model, thermal_model,
                                                           global_model, mo)

    global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                    environment_specification,
                                                                    simulation_specification)

    simulation_result = scheduler.simulate(global_specification, simulation_kernel)

    output = scenario_description.get("output")

    output_path = output.get("path")
    output_base_name = output.get("baseName")

    for i in output.get("generate"):
        if i == "allocationAndExecution":
            plot_cpu_utilization(global_specification, simulation_result,
                                 os.path.join(output_path, output_base_name + "cpu_utilization.png"))
            plot_task_execution(global_specification, simulation_result,
                                os.path.join(output_path, output_base_name + "task_execution.png"))
            plot_cpu_temperature(global_specification, simulation_result,
                                 os.path.join(output_path, output_base_name + "cpu_temperature.png"))
            plot_accumulated_execution_time(global_specification, simulation_result,
                                            os.path.join(output_path,
                                                         output_base_name + "accumulated_execution_time.png"))

        elif i == "temperatureEvolution":
            draw_heat_matrix(global_specification, simulation_kernel, simulation_result,
                             os.path.join(output_path, output_base_name + "heat_matrix.mp4"))


if __name__ == "__main__":
    # get and parse arguments passed to main
    # Add as many args as you need ...
    parser = argparse.ArgumentParser(description='Configure simulation scenario')
    parser.add_argument("-f", "--file", help="path to find description file", required=True)
    args = parser.parse_args()
    main(args)
    exit()
