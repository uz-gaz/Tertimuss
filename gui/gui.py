import tkinter as tk
import tkinter.ttk as ttk
from typing import Optional

from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification

# TODO: Do no thermal gui
from core.schedulers.abstract_scheduler import AbstractScheduler
from core.schedulers.scheduler_naming_selector import select_scheduler


class InputValidationError(Exception):
    """
    Basic exception class usen when input is incorrect
    """
    pass


class Validators(object):
    @staticmethod
    def is_integer_validator(to_validate: str, min_value: Optional[int] = None) -> bool:
        try:
            integer_result = int(to_validate)
            if min_value is not None:
                return integer_result > min_value
        except ValueError:
            return False

    @staticmethod
    def is_float_validator(to_validate: str, min_value: float = -float("inf")) -> bool:
        try:
            return float(to_validate) > min_value
        except ValueError:
            return False


class EnvironmentSpecificationControl(ttk.Frame):
    """
    Control of the environment specification input
    """

    def __init__(self, parent):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        # Validators
        float_positive_validator = (self.register(lambda x: Validators.is_float_validator(x, 0)), '%P')
        float_temperature_validator = (self.register(lambda x: Validators.is_float_validator(x, -273.15)), '%P')

        # h: Convection factor (W/mm^2 ºC)
        self.h_label = ttk.Label(self, text="Convection factor (W/mm^2 ºC): ")
        self.h_label.grid(column=0, row=0)

        self.h_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.h_entry.grid(column=1, row=0)

        # t_env: Environment temperature (ºC)
        self.t_env_label = ttk.Label(self, text="Environment temperature (ºC): ")
        self.t_env_label.grid(column=0, row=1)

        self.t_env_entry = ttk.Entry(self, validatecommand=float_temperature_validator, validate='none')
        self.t_env_entry.grid(column=1, row=1)

        # t_max: Maximum temperature (ºC)
        self.t_max_label = ttk.Label(self, text="Maximum temperature (ºC): ")
        self.t_max_label.grid(column=0, row=2)

        self.t_max_entry = ttk.Entry(self, validatecommand=float_temperature_validator, validate='none')
        self.t_max_entry.grid(column=1, row=2)

    def get_specification(self) -> EnvironmentSpecification:
        """
        Get the specification if is valid, raise an exception otherwise
        :return: the specification
        """
        # Check fields
        invalid_fields = []
        if not self.h_entry.validate():
            invalid_fields += ["Convection factor"]
        if not self.t_env_entry.validate():
            invalid_fields += ["Environment temperature"]
        if not self.t_max_entry.validate():
            invalid_fields += ["Maximum temperature"]

        # Return
        if len(invalid_fields) > 0:
            raise InputValidationError(invalid_fields)
        else:
            h: float = float(self.h_entry.get())
            t_max: float = float(self.t_max_entry.get())
            t_env: float = float(self.t_env_entry.get())
            return EnvironmentSpecification(h, t_env, t_max)


class SimulationSpecificationControl(ttk.Frame):
    """
    Control of the simulation specification input
    """

    def __init__(self, parent):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        # Validators
        float_positive_validator = (self.register(lambda x: Validators.is_float_validator(x, 0)), '%P')

        # step: Mesh step size (mm)
        self.step_label = ttk.Label(self, text="Mesh step size (mm): ")
        self.step_label.grid(column=0, row=0)

        self.step_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.step_entry.grid(column=1, row=0)

        # dt:  Accuracy (s)
        self.dt_label = ttk.Label(self, text="Accuracy (s): ")
        self.dt_label.grid(column=0, row=1)

        self.dt_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.dt_entry.grid(column=1, row=1)

    def get_specification(self) -> SimulationSpecification:
        """
        Get the specification if is valid, raise an exception otherwise
        :return: the specification
        """
        # Check fields
        invalid_fields = []
        if not self.step_entry.validate():
            invalid_fields += ["Mesh step size"]
        if not self.dt_entry.validate():
            invalid_fields += ["Accuracy"]

        # Return
        if len(invalid_fields) > 0:
            raise InputValidationError(invalid_fields)
        else:
            step: float = float(self.step_entry.get())
            dt: float = float(self.dt_entry.get())
            return SimulationSpecification(step, dt)


class SchedulerSpecificationControl(ttk.Frame):
    """
    Control of the scheduler specification input
    """

    def __init__(self, parent):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        self.scheduler_algorithm_label = ttk.Label(self, text="Scheduler algorithm: ")
        self.scheduler_algorithm_label.grid(column=0, row=0)

        self.scheduler_algorithm_combobox = ttk.Combobox(self, state="readonly")
        self.scheduler_algorithm_combobox["values"] = ["Global earliest deadline first",
                                                       "Global earliest deadline first less context changes",
                                                       "Based on TCPN model",
                                                       "Thermal Aware"]
        self.scheduler_algorithm_combobox.grid(column=0, row=1)

    def get_specification(self) -> AbstractScheduler:
        """
        Get the specification if is valid, raise an exception otherwise
        :return: the specification
        """

        # Scheduler definition name-id association
        schedulers_definition_thermal = {
            "Global earliest deadline first": "global_edf_scheduler",
            "Global earliest deadline first less context changes": "global_edf_affinity_scheduler",
            "Based on TCPN model": "rt_tcpn_scheduler",
            "Thermal Aware": "rt_tcpn_thermal_aware_scheduler"
        }

        # Check fields
        invalid_fields = []
        if self.scheduler_algorithm_combobox.get() == "":
            invalid_fields += ["Scheduler algorithm"]

        # Return
        if len(invalid_fields) > 0:
            raise InputValidationError(invalid_fields)
        else:
            return select_scheduler(schedulers_definition_thermal.get(self.scheduler_algorithm_combobox.get()), True)


class TaskSpecificationControl(ttk.Frame):
    """
    Control of the tasks specification input
    """

    # TODO: Validate fields and do getspecification
    def __init__(self, parent):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        # Validators
        float_positive_validator = (self.register(lambda x: Validators.is_float_validator(x, 0)), '%P')
        float_temperature_validator = (self.register(lambda x: Validators.is_float_validator(x, -273.15)), '%P')

        # Task list
        self.tasks_list = ttk.Treeview(self, columns=("t", "e"))
        self.tasks_list.grid(column=0, row=0, columnspan=2, rowspan=4)
        # self.tasks_list.insert("", tk.END, text="README.txt", values=("850 bytes", "18:30"))

        self.tasks_list.heading("#0", text="Worst case execution time")
        self.tasks_list.heading("t", text="Task period")
        self.tasks_list.heading("e", text="Energy consumption")

        # Task list add
        # c: Task worst case execution time in CPU cycles
        self.c_label = ttk.Label(self, text="Worst case execution time: ")
        self.c_label.grid(column=0, row=4)

        self.c_entry = ttk.Entry(self)
        self.c_entry.grid(column=1, row=4)

        # t: Task period, equal to deadline
        self.t_label = ttk.Label(self, text="Task period, equal to deadline: ")
        self.t_label.grid(column=0, row=5)

        self.t_entry = ttk.Entry(self)
        self.t_entry.grid(column=1, row=5)

        # e: Energy consumption
        self.e_label = ttk.Label(self, text="Energy consumption: ")
        self.e_label.grid(column=0, row=6)

        self.e_entry = ttk.Entry(self)
        self.e_entry.grid(column=1, row=6)

        # Add and delete task
        self.delete_task_button = ttk.Button(self, text="Delete selected")
        self.delete_task_button.grid(column=0, row=7)

        self.add_task_button = ttk.Button(self, text="Add")
        self.add_task_button.grid(column=1, row=7)

        #########################################
        # Separator
        self.sections_separator = ttk.Separator(self, orient="horizontal")
        self.sections_separator.grid(column=2, row=0)

        #########################################

        # Automatic task generation label
        self.automatic_task_generation_label = ttk.Label(self, text="Automatic task generation")
        self.automatic_task_generation_label.grid(column=3, row=0)

        # Task generation algorithm
        self.task_generation_algorithm_label = ttk.Label(self, text="Task generation algorithm: ")
        self.task_generation_algorithm_label.grid(column=3, row=1)

        self.task_generation_algorithm_combobox = ttk.Combobox(self, state="readonly")
        self.task_generation_algorithm_combobox["values"] = ["UUniFast"]
        self.task_generation_algorithm_combobox.grid(column=4, row=1)

        # Number of tasks
        self.number_of_task_label = ttk.Label(self, text="Number of tasks: ")
        self.number_of_task_label.grid(column=3, row=2)

        self.number_of_task_entry = ttk.Entry(self)
        self.number_of_task_entry.grid(column=4, row=2)

        # Utilization
        self.utilization_label = ttk.Label(self, text="Utilization: ")
        self.utilization_label.grid(column=3, row=3)

        self.utilization_entry = ttk.Entry(self)
        self.utilization_entry.grid(column=4, row=3)

        # Interval for periods
        self.interval_for_periods_label = ttk.Label(self, text="Interval for periods: ")
        self.interval_for_periods_label.grid(column=3, row=4)

        self.interval_for_periods_start_entry = ttk.Entry(self)
        self.interval_for_periods_start_entry.grid(column=4, row=4)

        self.interval_for_periods_end_entry = ttk.Entry(self)
        self.interval_for_periods_end_entry.grid(column=5, row=4)

        # Generate
        self.generate_button = ttk.Button(self, text="Generate")
        self.generate_button.grid(column=5, row=5)


class CpuSpecificationControl(ttk.Frame):
    """
    Control of the cpu specification input
    """

    # TODO: Validate fields and do getspecification
    def __init__(self, parent):
        """
        :param parent: The parent window
        """
        super().__init__(parent)
        # m: Number of CPU
        self.m_label = ttk.Label(self, text="Number of CPU: ")
        self.m_label.grid(column=0, row=0)

        self.m_entry = ttk.Entry(self)
        self.m_entry.grid(column=1, row=0)

        # f: Frequency
        self.f_label = ttk.Label(self, text="Frequency: ")
        self.f_label.grid(column=0, row=1)

        self.f_entry = ttk.Entry(self)
        self.f_entry.grid(column=1, row=1)

        #########################################
        # Separator
        self.sections_separator = ttk.Separator(self, orient="vertical")
        self.sections_separator.grid(column=2, row=0, rowspan=2, sticky="ns")
        #########################################

        # Board specification
        self.board_specification_label = ttk.Label(self, text="Board specification")
        self.board_specification_label.grid(column=3, row=0)

        # x(mm)
        self.x_board_label = ttk.Label(self, text="x(mm)")
        self.x_board_label.grid(column=3, row=1)

        self.x_board_entry = ttk.Entry(self)
        self.x_board_entry.grid(column=4, row=1)
        # y(mm)
        self.y_board_label = ttk.Label(self, text="y(mm)")
        self.y_board_label.grid(column=3, row=2)

        self.y_board_entry = ttk.Entry(self)
        self.y_board_entry.grid(column=4, row=2)

        # z(mm)
        self.z_board_label = ttk.Label(self, text="z(mm)")
        self.z_board_label.grid(column=3, row=3)

        self.z_board_entry = ttk.Entry(self)
        self.z_board_entry.grid(column=4, row=3)

        # p: Density (Kg/cm^3)
        self.p_board_label = ttk.Label(self, text="Density (Kg/cm^3)")
        self.p_board_label.grid(column=3, row=4)

        self.p_board_entry = ttk.Entry(self)
        self.p_board_entry.grid(column=4, row=4)

        # c_p: Specific heat capacities (J/Kg K)
        self.c_p_board_label = ttk.Label(self, text="Specific heat capacities (J/Kg K)")
        self.c_p_board_label.grid(column=3, row=5)

        self.c_p_board_entry = ttk.Entry(self)
        self.c_p_board_entry.grid(column=4, row=5)

        # k: Thermal conductivity (W/m ºC)
        self.k_board_label = ttk.Label(self, text="Thermal conductivity (W/m ºC)")
        self.k_board_label.grid(column=3, row=6)

        self.k_board_entry = ttk.Entry(self)
        self.k_board_entry.grid(column=4, row=6)

        #########################################
        # Separator
        self.sections_separator_2 = ttk.Separator(self, orient="horizontal")
        self.sections_separator_2.grid(column=3, row=7, columnspan=2, sticky="we")
        #########################################

        # CPU specification
        self.board_specification_label = ttk.Label(self, text="CPU specification")
        self.board_specification_label.grid(column=3, row=8)

        # x(mm)
        self.x_cpu_label = ttk.Label(self, text="x(mm)")
        self.x_cpu_label.grid(column=3, row=9)

        self.x_cpu_entry = ttk.Entry(self)
        self.x_cpu_entry.grid(column=4, row=9)
        # y(mm)
        self.y_cpu_label = ttk.Label(self, text="y(mm)")
        self.y_cpu_label.grid(column=3, row=10)

        self.y_cpu_entry = ttk.Entry(self)
        self.y_cpu_entry.grid(column=4, row=10)

        # z(mm)
        self.z_cpu_label = ttk.Label(self, text="z(mm)")
        self.z_cpu_label.grid(column=3, row=11)

        self.z_cpu_entry = ttk.Entry(self)
        self.z_cpu_entry.grid(column=4, row=11)

        # p: Density (Kg/cm^3)
        self.p_cpu_label = ttk.Label(self, text="Density (Kg/cm^3)")
        self.p_cpu_label.grid(column=3, row=12)

        self.p_cpu_entry = ttk.Entry(self)
        self.p_cpu_entry.grid(column=4, row=12)

        # c_p: Specific heat capacities (J/Kg K)
        self.c_p_cpu_label = ttk.Label(self, text="Specific heat capacities (J/Kg K)")
        self.c_p_cpu_label.grid(column=3, row=13)

        self.c_p_cpu_entry = ttk.Entry(self)
        self.c_p_cpu_entry.grid(column=4, row=13)

        # k: Thermal conductivity (W/m ºC)
        self.k_cpu_label = ttk.Label(self, text="Thermal conductivity (W/m ºC)")
        self.k_cpu_label.grid(column=3, row=14)

        self.k_cpu_entry = ttk.Entry(self)
        self.k_cpu_entry.grid(column=4, row=14)

        #########################################
        # Separator
        self.sections_separator_3 = ttk.Separator(self, orient="vertical")
        self.sections_separator_3.grid(column=5, row=7, rowspan=8, sticky="ns")
        #########################################

        # Origins location
        self.board_specification_label = ttk.Label(self, text="CPU origins location")
        self.board_specification_label.grid(column=6, row=8)

        self.tasks_list = ttk.Treeview(self, columns=("y"))
        self.tasks_list.grid(column=6, row=9, columnspan=2, rowspan=4)

        self.tasks_list.heading("#0", text="x(mm)")
        self.tasks_list.heading("y", text="y(mm)")

        # x
        self.x_label = ttk.Label(self, text="x: ")
        self.x_label.grid(column=6, row=14)

        self.x_entry = ttk.Entry(self)
        self.x_entry.grid(column=7, row=14)

        # y
        self.y_label = ttk.Label(self, text="y: ")
        self.y_label.grid(column=6, row=15)

        self.y_entry = ttk.Entry(self)
        self.y_entry.grid(column=7, row=15)

        # Add and delete task
        self.delete_task_button = ttk.Button(self, text="Delete selected")
        self.delete_task_button.grid(column=6, row=16)

        self.add_task_button = ttk.Button(self, text="Add")
        self.add_task_button.grid(column=7, row=16)

        # Automatic generate
        self.automatic_generate_button = ttk.Button(self, text="Automatic generate")
        self.automatic_generate_button.grid(column=7, row=17)


class SpecificationCategoriesControl(ttk.Frame):
    # TODO
    def __init__(self, parent):
        super().__init__(parent)

        self.notebook = ttk.Notebook(parent)
        self.notebook.place(x=0, y=0)
        self.place(relwidth=1, relheight=1)

        # Crear el contenido de cada una de las pestañas.
        self.web_label = EnvironmentSpecificationControl(self.notebook)

        # Añadirlas al panel con su respectivo texto.
        self.notebook.add(self.web_label, text="Tab 1", padding=20)

        self.notebook.pack(padx=10, pady=10)
        self.pack(expand=True, fill=tk.BOTH)


class GraphicalUserInterface(ttk.Frame):
    # TODO
    def __init__(self, parent):
        super().__init__(parent)
        self.place(relwidth=1, relheight=1)
        self.task_specification = EnvironmentSpecificationControl(self)


if __name__ == '__main__':
    # TODO
    window = tk.Tk()
    window.title("Scheduler simulation Framework")
    window.configure(width=1200, height=700)
    gui = SchedulerSpecificationControl(window)
    # gui.place(relwidth=1, relheight=1)
    gui.grid(column=0, row=0)


    def specification_valid():
        try:
            gui.get_specification()
            print("All valid")
        except InputValidationError as ve:
            print("Fields: " + ', '.join(ve.args[0]))


    button_calc = tk.Button(window, text="Calculate", command=specification_valid)
    button_calc.grid(column=0, row=1)
    window.mainloop()
