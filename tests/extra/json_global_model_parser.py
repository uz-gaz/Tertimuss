import unittest

from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser


class JsonGlobalModelParserTest(unittest.TestCase):
    def test_json_global_model_parser(self):
        # Files
        input_file = "tests/cli/input-example-thermal-aperiodics-energy.json"
        schema_file = "main/ui/cli/input_schema/input-schema.json"

        # Json object
        input_object = JSONGlobalModelParser.read_input(input_file)
        schema_object = JSONGlobalModelParser.read_input(schema_file)

        # Validate the input
        error_validation, message_validation = JSONGlobalModelParser.validate_input(schema_object, input_object)

        # Get model and scheduler
        global_specification, scheduler, output_list, scenario_description_completed = \
            JSONGlobalModelParser.obtain_global_model(input_object)


if __name__ == '__main__':
    unittest.main()
