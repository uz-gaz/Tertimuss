import os
from typing import Optional

from main.core.tcpn_model_generator.GlobalModel import GlobalModel
from main.ui.cli.ProgressBarCli import ProgressBarCli

from main.ui.common.AbstractProgressBar import AbstractProgressBar
from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser


class CliController(object):
    @classmethod
    def cli_main(cls, args):
        # Progress bar
        if args.verbose:
            progress_bar: Optional[AbstractProgressBar] = ProgressBarCli()
        else:
            progress_bar: Optional[AbstractProgressBar] = None

        # Path of the input validate schema
        input_schema_path = './input_schema/input-schema.json'
        absolute_input_schema_path = os.path.join(os.path.dirname(__file__), input_schema_path)

        # Read schema for validation
        if args.verbose:
            progress_bar.update("Data loading", 0)

        # Read schema
        error, message, schema_object = JSONGlobalModelParser.read_input(absolute_input_schema_path)

        if error:
            print(message)
            return 1

        # Read input
        error, message, input_object = JSONGlobalModelParser.read_input(args.file)

        if error:
            print(message)
            return 1

        # Validate schema
        error, message = JSONGlobalModelParser.validate_input(input_object, schema_object)

        if error:
            print(message)
            return 1

        if args.verbose:
            progress_bar.update_progress(100)
            progress_bar.update("Creating global model", 0)

        # Get model and scheduler
        global_specification, scheduler, output_path, output_list, scenario_description_completed = \
            JSONGlobalModelParser.obtain_global_model(input_object)

        # Create output directory if not exist
        os.makedirs(output_path, exist_ok=True)

        # Create global model
        try:
            global_model = GlobalModel(global_specification)
        except Exception as ex:
            print(ex)
            return 1

        if args.verbose:
            progress_bar.update_progress(100)
            progress_bar.update("Scheduling", 0)

        try:
            scheduler_result = scheduler.simulate(global_specification, global_model, progress_bar)
        except Exception as ex:
            print(ex)
            return 1

        if args.verbose:
            progress_bar.update_progress(100)
            progress_bar.close()

        # Print scheduler result
        for i in output_list:
            output_drawer, options = i
            output_drawer.plot(global_specification, scheduler_result, options)
