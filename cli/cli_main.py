import argparse
import json
from jsonschema import validate, ValidationError


def main(args):
    # Path of the input validate schema
    input_schema_path = "input-schema-v1.0.json"

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
    except ValidationError:
        print("Error: Wrong fields validation in ", args.file)
        return 1

    specifications = []
    # Create problem instances
    for problem_specification in scenario_description:
        # TODO: Fill actual specification
        pass

    for problem_specification in specifications:
        # TODO: Create process to solve actual specification (Create thread pool)
        pass

    # TODO: Join all process


if __name__ == "__main__":
    # get and parse arguments passed to main
    # Add as many args as you need ...
    parser = argparse.ArgumentParser(description='Configure simulation scenario')
    parser.add_argument("-f", "--file", help="path to find description file", required=True)
    args = parser.parse_args()
    main(args)
    exit()
