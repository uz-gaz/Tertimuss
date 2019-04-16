import argparse
import json
from jsonschema import validate, ValidationError

from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid, Origin, check_origins


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

    processor = scenario_description.get("processor")

    board_prop = processor.get("boardProperties")
    board_physical_properties = board_prop.get("physicalProperties")

    core_properties = processor.get("coresProperties")
    core_physical_properties = core_properties.get("physicalProperties")

    cpu_origins = core_properties.get("coresOrigins")

    if cpu_origins is not None:
        cpu_origins = list(map(lambda x: Origin(x.get("x"), x.get("y")), cpu_origins))

        if not check_origins(cpu_origins):
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

    ii = 0

    # specifications = []
    #  Create problem instances
    # for problem_specification in scenario_description:
    #     # TODO: Fill actual specification
    #    pass

    # for problem_specification in specifications:
    #     # TODO: Create process to solve actual specification (Create thread pool)
    #     pass

    # # TODO: Join all process


if __name__ == "__main__":
    # get and parse arguments passed to main
    # Add as many args as you need ...
    parser = argparse.ArgumentParser(description='Configure simulation scenario')
    parser.add_argument("-f", "--file", help="path to find description file", required=True)
    args = parser.parse_args()
    main(args)
    exit()
