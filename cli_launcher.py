import argparse

from main.ui.cli.cli_main import cli_main

if __name__ == "__main__":
    # Get scenario specification and pass it to the main
    parser = argparse.ArgumentParser(description='Configure simulation scenario')
    parser.add_argument("-f", "--file", help="path to find description file", required=True)
    parser.add_argument("-v", "--verbose", help="show progress", required=False, action='store_true')
    arguments = parser.parse_args()
    cli_main(arguments)
    exit()
