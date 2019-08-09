import json
import unittest
import os.path

from jsonschema import RefResolver, Draft7Validator

from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser


class JSONGlobalModelParserTest(unittest.TestCase):
    # @staticmethod
    # def _load_json_schema(schemas_path_base_name: str, schema_name: str):
    #     """ Loads the given schema file """
    #
    #     relative_path = os.path.join(schemas_path_base_name, schema_name)
    #     absolute_path = os.path.join(os.path.dirname(__file__), relative_path)
    #
    #     base_path = os.path.dirname(absolute_path)
    #     base_uri = 'file://{}/'.format(base_path)
    #
    #     with open(absolute_path) as schema_file:
    #         return jsonref.loads(schema_file.read(), base_uri=base_uri, jsonschema=True)

    def test_json_validator(self):
        input_path = "../../tests/cli/input-example-thermal-aperiodics-energy.json"
        schema_name = "input-schema.json"
        schema_base_path = "../../main/ui/cli/input_schema"

        relative_schema_path = os.path.join(schema_base_path, schema_name)
        absolute_schema_path = os.path.join(os.path.dirname(__file__), relative_schema_path)

        with open(absolute_schema_path, 'r') as fp:
            schema = json.load(fp)

        resolver = RefResolver(
            # The key part is here where we build a custom RefResolver
            # and tell it where *this* schema lives in the filesystem
            # Note that `file:` is for unix systems
            'file://'.format(schema), schema
        )
        Draft7Validator.check_schema(schema)  # Unnecessary but a good idea
        validator = Draft7Validator(schema, resolver=resolver, format_checker=None)

        input_json = JSONGlobalModelParser.read_input(input_path)

        validator.validate(input_json)


        schema_json = self._load_json_schema(schema_base_path, schema_name)
        JSONGlobalModelParser.validate_input(input_json, schema_json)

        i = 0


if __name__ == '__main__':
    unittest.main()
