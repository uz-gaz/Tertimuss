import os
import unittest

import jsonschema

from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser


class JsonParserTest(unittest.TestCase):
    def test_json_parser(self):
        # File to test
        file_to_test_path = os.path.join('input-example-no-thermal-10-taks.json')
        absolute_file_to_test_path = os.path.join(os.path.dirname(__file__), file_to_test_path)

        # Path of the input validate schema
        input_schema_path = os.path.join('../..', '..', 'main', 'ui', 'cli', 'input_schema', 'global-schema.json')
        absolute_input_schema_path = os.path.join(os.path.dirname(__file__), input_schema_path)

        # Read schema
        error, message, schema_object = JSONGlobalModelParser.read_input(absolute_input_schema_path)

        if error:
            print(message)
            assert False

        # Read input
        error, message, input_object = JSONGlobalModelParser.read_input(absolute_file_to_test_path)

        if error:
            print(message)
            assert False

        # Validate schema
        resolver = jsonschema.RefResolver('file://%s/' % os.path.abspath(os.path.dirname(absolute_input_schema_path)),
                                          None)
        error, message = JSONGlobalModelParser.validate_input(input_object, schema_object, resolver)

        if error:
            print(message)
            assert False


if __name__ == '__main__':
    unittest.main()
