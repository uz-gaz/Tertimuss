# System requirements
This project has been developed using the Miniconda Python distribution with a Python version 3.7 installed (Can be downloaded from: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)).

It's highly recommended to use the same Python distribution (or Anaconda) to avoid issues related with dependencies. However you can use another of your choice.

## Project dependencies (libraries)
The project needs the follow packages:

- Python 3.7 or higher and all its dependencies
- scipy 1.3.0 or higher and all its dependencies
- matplotlib 3.0.2 or higher and all its dependencies
- jsonschema 3.0.1 or higher and all its dependencies
- progress 1.5 or higher and all its dependencies
- ffmpeg 4.1 or higher and all its dependencies
- pyqt 5.9.2 or higher and all its dependencies
- qt 5.9.2 or higher and all its dependencies (This package is necessary only if you want to modify the GUI)
- nodejs 10.13.0 or higher and all its dependencies  (This package is necessary only if you want to modify the CLI JSON input)


If you are using Miniconda or Anaconda the next few lines will create an environment called rt-scheduler-simulation-environment with all project dependencies installed in it.

```bash
$ conda create -n rt-scheduler-simulation-environment python=3 scipy matplotlib jsonschema pyqt qt nodejs
$ conda activate rt-scheduler-simulation-environment
$ conda install -c conda-forge ffmpeg progress
```

# Usage
Once you have filled the requirements listed in the above section and have downloaded the repository, place in the project root folder.

There are two python Scripts, one for the Command Line Interface and other for the Graphical User Interface.

## Command Line Interface
To launch the Command Line Interface execute the script called cli_launcher.py.

This script takes two arguments
- -f, --file: Path where find the JSON simulation description file. This file must accomplish the JSON SCHEMA specification located in ./cli/input-schema/input-schema.json (some examples are located in ./tests/cli)
- -v, --verbose \[Optional\] : Display simulation progress and execution time

```bash
$ python cli_launcher.py
```

## Graphical User Interface
To launch the Graphical User Interface execute the script called gui_launcher.py.

```bash
$ python gui_launcher.py
```

# For developers only
## Modifications in the schema to validate the input of the CLI
Each time you modify any file of the schema to validate the input, you must recompile it:
```bash
$ cd main/ui/common/json_ref_parser
$ npm run parse-json ../../cli/input_schema/global-schema.json ../../cli/input_schema/input-schema.json
```

## Modifications on the GUI
To modify the GUI is recommended to use the Qt Designer.

To launch it execute the following command:
```bash
$ designer
```

One you have modified the XML (.ui) file that you create with Qt Designer, you have to transform it to a Python file.
To do it, just execute the following command (changing foo and bar for the files names):

```bash
$ pyuic5 foo.ui -o bar.py
```

## Add a new scheduler to the environment
To add a new scheduler to the environment, you have to create a new class in the main.core.schedulers.implementations package that extends from main.core.schedulers.templates.abstract_base_scheduler.AbstractBaseScheduler or from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler.

Next, you have to add his name to the main.ui.common.SchedulerSelector class.


