import os
import unittest
from typing import Dict

import jsonschema
from jsonschema import ValidationError

from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser


class JsonParserTest(unittest.TestCase):
    @staticmethod
    def validate_input(input_json: Dict, schema_json: Dict, resolverSchema) -> [bool, str]:
        """
        Check if input_json conforms to scheme schema_json
        :param input_json: JSON as a Dict object
        :param schema_json: JSON schema as a Dict object
        :return: 1 -> True if there was an error
                 2 -> Error message
        """
        # Validate the input
        try:
            jsonschema.validate(input_json, schema_json, resolver=resolverSchema)
            return False, ""
        except ValidationError as ve:
            return True, 'Error: Wrong fields validation in ' + '/'.join(map(lambda x: str(x), ve.absolute_path)) + \
                   ' with message ' + ve.message

    def test_json_parser(self):
        # File to test
        file_to_test_path = os.path.join('input-example-no-thermal-10-taks.json')
        absolute_file_to_test_path = os.path.join(os.path.dirname(__file__), file_to_test_path)

        # Path of the input validate schema
        # input_schema_path = os.path.join('..', '..', 'main', 'ui', 'cli', 'input_schema', 'input-schema.json')
        input_schema_path = os.path.join('..', '..', 'main', 'ui', 'cli', 'input_schema', 'global-schema.json')
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

        sSchemaDir = os.path.dirname(os.path.abspath(absolute_input_schema_path))
        print(os.path.dirname(os.path.abspath(absolute_input_schema_path)))
        oResolver = jsonschema.RefResolver(base_uri=sSchemaDir, referrer=schema_object)

        # Validate schema
        error, message = self.validate_input(input_object, schema_object, oResolver)

        if error:
            print(message)
            assert False


if __name__ == '__main__':
    unittest.main()
