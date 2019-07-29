import argparse

from main.ui.gui.GuiController import GuiController

if __name__ == "__main__":
    # Get scenario specification and pass it to the main
    parser = argparse.ArgumentParser(description='Configure simulation scenario')
    parser.add_argument("-nt", "--no-thermal", help="Run simulation without thermal", required=False,
                        action='store_true')
    arguments = parser.parse_args()

    GuiController.gui_main(arguments)
    exit()
