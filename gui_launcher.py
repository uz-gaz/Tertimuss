import argparse

from ui.gui.gui import gui_main

if __name__ == "__main__":
    # Get scenario specification and pass it to the main
    parser = argparse.ArgumentParser(description='Configure simulation scenario')
    parser.add_argument("-nt", "--no-thermal", help="Run simulation without thermal", required=False,
                        action='store_true')
    arguments = parser.parse_args()
    gui_main(not arguments.no_thermal)
    exit()
