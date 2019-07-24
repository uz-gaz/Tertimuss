from typing import Optional

from main.core.tcpn_model_generator.global_model import GlobalModel
from main.ui.cli.ProgressBarCli import ProgressBarCli

from main.ui.common.AbstractProgressBar import AbstractProgressBar
from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser


class CliManager(object):
    @classmethod
    def cli_main(cls, args):
        # Progress bar
        if args.verbose:
            progress_bar: Optional[AbstractProgressBar] = ProgressBarCli()
        else:
            progress_bar: Optional[AbstractProgressBar] = None

        # Path of the input validate schema
        # Warning: In python paths are relative to the entry point script path
        input_schema_path = './main/ui/cli/input_schema/input-schema.json'

        # Read schema for validation
        if args.verbose:
            progress_bar.update("Data loading", 0)

        # Read schema
        input_schema = JSONGlobalModelParser.read_input(input_schema_path)

        # Read input
        scenario_description = JSONGlobalModelParser.read_input(args.file)

        # Validate the input
        error_validation, message_validation = JSONGlobalModelParser.validate_input(input_schema, scenario_description)

        if args.verbose:
            progress_bar.update_progress(100)
            progress_bar.update("Creating global model", 0)

        if error_validation:
            print(message_validation)
            return 1

        # Get model and scheduler
        global_specification, scheduler, output_list, scenario_description_completed = \
            JSONGlobalModelParser.obtain_global_model(scenario_description)

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
