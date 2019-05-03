import os
import threading
import tkinter as tk
import tkinter.ttk as ttk
from enum import Enum
from multiprocessing import Process
from typing import Optional, Callable, List

from core.kernel_generator.global_model import generate_global_model
from core.kernel_generator.kernel import SimulationKernel
from core.kernel_generator.processor_model import ProcessorModel, generate_processor_model
from core.kernel_generator.tasks_model import TasksModel, generate_tasks_model
from core.kernel_generator.thermal_model import ThermalModel, generate_thermal_model
from core.problem_specification_models.CpuSpecification import CpuSpecification, Origin, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task
from core.schedulers.abstract_scheduler import AbstractScheduler
from core.schedulers.scheduler_naming_selector import select_scheduler
from core.task_generator.task_generator_naming_selector import select_task_generator

# TODO: Do no thermal gui
from output_generation.output_generator import plot_cpu_utilization, plot_task_execution, \
    plot_accumulated_execution_time, plot_cpu_temperature, draw_heat_matrix


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

        # Frame to get elements near
        self.frame_interior = ttk.Frame(self)
        self.frame_interior.grid(column=0, row=0)

        # h: Convection factor (W/mm^2 ºC)
        self.h_label = ttk.Label(self.frame_interior, text="Convection factor (W/mm^2 ºC): ")
        self.h_label.grid(column=0, row=0, pady=10, sticky="e")

        self.h_entry = ttk.Entry(self.frame_interior, validatecommand=float_positive_validator, validate='none')
        self.h_entry.grid(column=1, row=0, pady=10, sticky="ew", padx=10)

        # t_env: Environment temperature (ºC)
        self.t_env_label = ttk.Label(self.frame_interior, text="Environment temperature (ºC): ")
        self.t_env_label.grid(column=0, row=1, pady=10, sticky="e")

        self.t_env_entry = ttk.Entry(self.frame_interior, validatecommand=float_temperature_validator, validate='none')
        self.t_env_entry.grid(column=1, row=1, pady=10, sticky="ew", padx=10)

        # t_max: Maximum temperature (ºC)
        self.t_max_label = ttk.Label(self.frame_interior, text="Maximum temperature (ºC): ")
        self.t_max_label.grid(column=0, row=2, pady=10, sticky="e")

        self.t_max_entry = ttk.Entry(self.frame_interior, validatecommand=float_temperature_validator, validate='none')
        self.t_max_entry.grid(column=1, row=2, pady=10, sticky="ew", padx=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

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

        # Frame to get elements near
        self.frame_interior = ttk.Frame(self)
        self.frame_interior.grid(column=0, row=0)

        # step: Mesh step size (mm)
        self.step_label = ttk.Label(self.frame_interior, text="Mesh step size (mm): ")
        self.step_label.grid(column=0, row=0, pady=10, sticky="e")

        self.step_entry = ttk.Entry(self.frame_interior, validatecommand=float_positive_validator, validate='none')
        self.step_entry.grid(column=1, row=0, pady=10, sticky="ew", padx=10)

        # dt:  Accuracy (s)
        self.dt_label = ttk.Label(self.frame_interior, text="Accuracy (s): ")
        self.dt_label.grid(column=0, row=1, pady=10, sticky="e")

        self.dt_entry = ttk.Entry(self.frame_interior, validatecommand=float_positive_validator, validate='none')
        self.dt_entry.grid(column=1, row=1, pady=10, sticky="ew", padx=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

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

        # Frame to get elements near
        self.frame_interior = ttk.Frame(self)
        self.frame_interior.grid(column=0, row=0)

        self.scheduler_algorithm_label = ttk.Label(self.frame_interior, text="Scheduler algorithm: ")
        self.scheduler_algorithm_label.grid(column=0, row=0, sticky="e")

        self.scheduler_algorithm_combobox = ttk.Combobox(self.frame_interior, state="readonly")
        self.scheduler_algorithm_combobox["values"] = ["Glob. earliest deadline first",
                                                       "G-EDF less context changes",
                                                       "Based on TCPN model",
                                                       "Thermal Aware"]
        self.scheduler_algorithm_combobox.grid(column=1, row=0, pady=10, sticky="ew", padx=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def get_specification(self) -> AbstractScheduler:
        """
        Get the specification if is valid, raise an exception otherwise
        :return: the specification
        """

        # Scheduler definition name-id association
        schedulers_definition_thermal = {
            "Glob. earliest deadline first": "global_edf_scheduler",
            "G-EDF less context changes": "global_edf_affinity_scheduler",
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

    def __init__(self, parent, internal_error_handler: Callable[[List[str]], None]):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        # Validators
        float_positive_validator = (self.register(lambda x: Validators.is_float_validator(x, 0)), '%P')
        integer_positive_validator = (self.register(lambda x: Validators.is_integer_validator(x, 0)), '%P')

        # Manual task generation label
        self.manual_task_generation_label = ttk.Label(self, text="Manual task generation")
        self.manual_task_generation_label.grid(column=0, row=0, columnspan=3, pady=10)

        # Task list
        self.tasks_list = ttk.Treeview(self, columns=("t", "e"))
        self.tasks_list.grid(column=0, row=1, columnspan=3, rowspan=6, padx=10)
        # self.tasks_list.insert("", tk.END, text="README.txt", values=("850 bytes", "18:30"))

        self.tasks_list.heading("#0", text="Worst case execution time")
        self.tasks_list.heading("t", text="Task period")
        self.tasks_list.heading("e", text="Energy consumption")

        # Task list add
        # c: Task worst case execution time in CPU cycles
        self.c_label = ttk.Label(self, text="Worst case execution time: ")
        self.c_label.grid(column=1, row=7, pady=10, sticky="e")

        self.c_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.c_entry.grid(column=2, row=7, pady=10, sticky="ew", padx=10)

        # t: Task period, equal to deadline
        self.t_label = ttk.Label(self, text="Task period, equal to deadline: ")
        self.t_label.grid(column=1, row=8, pady=10, sticky="e")

        self.t_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.t_entry.grid(column=2, row=8, pady=10, sticky="ew", padx=10)

        # e: Energy consumption
        self.e_label = ttk.Label(self, text="Energy consumption: ")
        self.e_label.grid(column=1, row=9, pady=10, sticky="e")

        self.e_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.e_entry.grid(column=2, row=9, pady=10, sticky="ew", padx=10)

        # Add and delete task

        self.add_task_button = ttk.Button(self, text="Add",
                                          command=lambda: self.add_task_callback(internal_error_handler))
        self.add_task_button.grid(column=2, row=10, sticky="ew", padx=10)

        self.delete_task_button = ttk.Button(self, text="Delete selected",
                                             command=self.delete_task_callback)
        self.delete_task_button.grid(column=2, row=11, sticky="ew", padx=10, pady=10)

        #########################################
        # Separator
        self.sections_separator = ttk.Separator(self, orient="vertical")
        self.sections_separator.grid(column=3, row=0, rowspan=12, padx=10, sticky="ns")

        #########################################

        # Automatic task generation label
        self.automatic_task_generation_label = ttk.Label(self, text="Automatic task generation")
        self.automatic_task_generation_label.grid(column=4, row=0, columnspan=3)

        # Task generation algorithm
        self.task_generation_algorithm_label = ttk.Label(self, text="Task generation algorithm: ")
        self.task_generation_algorithm_label.grid(column=4, row=1, pady=10, sticky="e")

        self.task_generation_algorithm_combobox = ttk.Combobox(self, state="readonly")
        self.task_generation_algorithm_combobox["values"] = ["UUniFast"]
        self.task_generation_algorithm_combobox.grid(column=5, row=1, columnspan=2, pady=10, sticky="ew", padx=10)

        # Number of tasks
        self.number_of_task_label = ttk.Label(self, text="Number of tasks: ")
        self.number_of_task_label.grid(column=4, row=2, pady=10, sticky="e")

        self.number_of_task_entry = ttk.Entry(self, validatecommand=integer_positive_validator, validate='none')
        self.number_of_task_entry.grid(column=5, row=2, columnspan=2, pady=10, sticky="ew", padx=10)

        # Utilization
        self.utilization_label = ttk.Label(self, text="Utilization: ")
        self.utilization_label.grid(column=4, row=3, pady=10, sticky="e")

        self.utilization_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.utilization_entry.grid(column=5, row=3, columnspan=2, pady=10, sticky="ew", padx=10)

        # Interval for periods
        self.interval_for_periods_label = ttk.Label(self, text="Interval for periods: ")
        self.interval_for_periods_label.grid(column=4, row=4, pady=10, sticky="e")

        self.interval_for_periods_start_entry = ttk.Entry(self, validatecommand=float_positive_validator,
                                                          validate='none')
        self.interval_for_periods_start_entry.grid(column=5, row=4, pady=10, sticky="ew", padx=10)

        self.interval_for_periods_end_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.interval_for_periods_end_entry.grid(column=6, row=4, pady=10, sticky="ew", padx=10)

        # Generate
        self.generate_button = ttk.Button(self, text="Generate",
                                          command=lambda: self.generate_automatic_tasks(internal_error_handler))
        self.generate_button.grid(column=6, row=5, pady=10, sticky="ew", padx=10)

    def add_task_callback(self, internal_error_handler: Callable[[List[str]], None]):
        """
        Add the task to the task list if is valid
        :param internal_error_handler: Error handler
        """
        # Check fields
        invalid_fields = []
        if not self.c_entry.validate():
            invalid_fields += ["Worst case execution time"]
        if not self.t_entry.validate():
            invalid_fields += ["Task period"]
        if not self.e_entry.validate():
            invalid_fields += ["Energy consumption"]

        # Add task
        internal_error_handler(invalid_fields)

        if len(invalid_fields) == 0:
            self.tasks_list.insert("", tk.END, text=self.c_entry.get(), values=(self.t_entry.get(), self.e_entry.get()))
            self.c_entry.delete(0, 'end')
            self.t_entry.delete(0, 'end')
            self.e_entry.delete(0, 'end')

    def delete_task_callback(self):
        """
        Delete selected tasks from the tasks list
        """
        self.tasks_list.delete(*self.tasks_list.selection())

    def generate_automatic_tasks(self, internal_error_handler: Callable[[List[str]], None]):
        """
        Generate automatic task list
        :param internal_error_handler: Error handler
        """

        # Task generation definition name-id association
        task_generator_definition = {
            "UUniFast": "uunifast"
        }

        # Check fields
        invalid_fields = []
        if self.task_generation_algorithm_combobox.get() == "":
            invalid_fields += ["Task generation algorithm"]
        if not self.number_of_task_entry.validate():
            invalid_fields += ["Number of tasks"]
        if not self.utilization_entry.validate():
            invalid_fields += ["Utilization"]
        if not self.interval_for_periods_start_entry.validate() or not self.interval_for_periods_end_entry.validate() \
                or float(
            self.interval_for_periods_start_entry.get()) > float(self.interval_for_periods_end_entry.get()):
            invalid_fields += ["Interval for periods"]

        # Add task
        if len(invalid_fields) > 0:
            internal_error_handler(invalid_fields)
        else:
            tasks_generator = select_task_generator(
                task_generator_definition.get(self.task_generation_algorithm_combobox.get()),
                int(self.number_of_task_entry.get()),
                float(self.utilization_entry.get()), (
                    float(self.interval_for_periods_start_entry.get()),
                    float(self.interval_for_periods_end_entry.get())),
                1)  # FIXME: Now is always using frequency 1, think if other situation may be better
            tasks = tasks_generator.generate()

            # Clear tasks list
            self.tasks_list.delete(*self.tasks_list.get_children())

            # Add new tasks
            for i in tasks:
                self.tasks_list.insert("", tk.END, text=i.c, values=(i.t, i.e))

    def get_specification(self) -> TasksSpecification:
        """
        Get the specification if is valid, raise an exception otherwise
        :return: the specification
        """
        # Check fields
        invalid_fields = []
        if len(self.tasks_list.get_children()) == 0:
            invalid_fields += ["Tasks"]

        # Return
        if len(invalid_fields) > 0:
            raise InputValidationError(invalid_fields)
        else:
            return TasksSpecification([Task(float(self.tasks_list.item(i).get("text")),
                                            int(self.tasks_list.item(i).get("values")[0]),
                                            float(self.tasks_list.item(i).get("values")[1])) for i in
                                       self.tasks_list.get_children()])


class CpuSpecificationControl(ttk.Frame):
    """
    Control of the cpu specification input
    """

    def __init__(self, parent, internal_error_handler: Callable[[List[str]], None]):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        # Validators
        float_positive_validator = (self.register(lambda x: Validators.is_float_validator(x, 0)), '%P')
        integer_positive_validator = (self.register(lambda x: Validators.is_integer_validator(x, 0)), '%P')

        # Frame to get elements near
        self.frame_interior_1 = ttk.Frame(self)
        self.frame_interior_1.grid(column=0, row=0, columnspan=2)

        # CPU specification
        self.board_specification_label = ttk.Label(self.frame_interior_1, text="CPU specification")
        self.board_specification_label.grid(column=0, row=0, pady=10, columnspan=2)

        # m: Number of CPU
        self.m_label = ttk.Label(self.frame_interior_1, text="Number of CPU: ")
        self.m_label.grid(column=0, row=1, pady=10, sticky="e")

        self.m_entry = ttk.Entry(self.frame_interior_1, validatecommand=integer_positive_validator, validate='none')
        self.m_entry.grid(column=1, row=1, pady=10, sticky="ew", padx=10)

        # f: Frequency
        self.f_label = ttk.Label(self.frame_interior_1, text="Frequency: ")
        self.f_label.grid(column=0, row=2, pady=10, sticky="e")

        self.f_entry = ttk.Entry(self.frame_interior_1, validatecommand=float_positive_validator, validate='none')
        self.f_entry.grid(column=1, row=2, pady=10, sticky="ew", padx=10)

        # Frame to get elements near
        self.frame_interior_2 = ttk.Frame(self)
        self.frame_interior_2.grid(column=1, row=1)

        # Board specification
        self.board_specification_label = ttk.Label(self.frame_interior_2, text="Board physical specification")
        self.board_specification_label.grid(column=0, row=0, pady=10, columnspan=2)

        # x(mm)
        self.x_board_label = ttk.Label(self.frame_interior_2, text="x(mm)")
        self.x_board_label.grid(column=0, row=1, pady=10, sticky="e")

        self.x_board_entry = ttk.Entry(self.frame_interior_2, validatecommand=float_positive_validator, validate='none')
        self.x_board_entry.grid(column=1, row=1, pady=10, sticky="ew", padx=10)
        # y(mm)
        self.y_board_label = ttk.Label(self.frame_interior_2, text="y(mm)")
        self.y_board_label.grid(column=0, row=2, pady=10, sticky="e")

        self.y_board_entry = ttk.Entry(self.frame_interior_2, validatecommand=float_positive_validator, validate='none')
        self.y_board_entry.grid(column=1, row=2, pady=10, sticky="ew", padx=10)

        # z(mm)
        self.z_board_label = ttk.Label(self.frame_interior_2, text="z(mm)")
        self.z_board_label.grid(column=0, row=3, pady=10, sticky="e")

        self.z_board_entry = ttk.Entry(self.frame_interior_2, validatecommand=float_positive_validator, validate='none')
        self.z_board_entry.grid(column=1, row=3, pady=10, sticky="ew", padx=10)

        # p: Density (Kg/cm^3)
        self.p_board_label = ttk.Label(self.frame_interior_2, text="Density (Kg/cm^3)")
        self.p_board_label.grid(column=0, row=4, pady=10, sticky="e")

        self.p_board_entry = ttk.Entry(self.frame_interior_2, validatecommand=float_positive_validator, validate='none')
        self.p_board_entry.grid(column=1, row=4, pady=10, sticky="ew", padx=10)

        # c_p: Specific heat capacities (J/Kg K)
        self.c_p_board_label = ttk.Label(self.frame_interior_2, text="Specific heat capacities (J/Kg K)")
        self.c_p_board_label.grid(column=0, row=5, pady=10, sticky="e")

        self.c_p_board_entry = ttk.Entry(self.frame_interior_2, validatecommand=float_positive_validator,
                                         validate='none')
        self.c_p_board_entry.grid(column=1, row=5, pady=10, sticky="ew", padx=10)

        # k: Thermal conductivity (W/m ºC)
        self.k_board_label = ttk.Label(self.frame_interior_2, text="Thermal conductivity (W/m ºC)")
        self.k_board_label.grid(column=0, row=6, pady=10, sticky="e")

        self.k_board_entry = ttk.Entry(self.frame_interior_2, validatecommand=float_positive_validator, validate='none')
        self.k_board_entry.grid(column=1, row=6, pady=10, sticky="ew", padx=10)

        # Frame to get elements near
        self.frame_interior_3 = ttk.Frame(self)
        self.frame_interior_3.grid(column=0, row=1)

        # CPU specification
        self.board_specification_label = ttk.Label(self.frame_interior_3, text="Core physical specification")
        self.board_specification_label.grid(column=0, row=0, pady=10, columnspan=2)

        # x(mm)
        self.x_cpu_label = ttk.Label(self.frame_interior_3, text="x(mm)")
        self.x_cpu_label.grid(column=0, row=2, pady=10, sticky="e")

        self.x_cpu_entry = ttk.Entry(self.frame_interior_3, validatecommand=float_positive_validator, validate='none')
        self.x_cpu_entry.grid(column=1, row=2, pady=10, sticky="ew", padx=10)
        # y(mm)
        self.y_cpu_label = ttk.Label(self.frame_interior_3, text="y(mm)")
        self.y_cpu_label.grid(column=0, row=3, pady=10, sticky="e")

        self.y_cpu_entry = ttk.Entry(self.frame_interior_3, validatecommand=float_positive_validator, validate='none')
        self.y_cpu_entry.grid(column=1, row=3, pady=10, sticky="ew", padx=10)

        # z(mm)
        self.z_cpu_label = ttk.Label(self.frame_interior_3, text="z(mm)")
        self.z_cpu_label.grid(column=0, row=4, pady=10, sticky="e")

        self.z_cpu_entry = ttk.Entry(self.frame_interior_3, validatecommand=float_positive_validator, validate='none')
        self.z_cpu_entry.grid(column=1, row=4, pady=10, sticky="ew", padx=10)

        # p: Density (Kg/cm^3)
        self.p_cpu_label = ttk.Label(self.frame_interior_3, text="Density (Kg/cm^3)")
        self.p_cpu_label.grid(column=0, row=5, pady=10, sticky="e")

        self.p_cpu_entry = ttk.Entry(self.frame_interior_3, validatecommand=float_positive_validator, validate='none')
        self.p_cpu_entry.grid(column=1, row=5, pady=10, sticky="ew", padx=10)

        # c_p: Specific heat capacities (J/Kg K)
        self.c_p_cpu_label = ttk.Label(self.frame_interior_3, text="Specific heat capacities (J/Kg K)")
        self.c_p_cpu_label.grid(column=0, row=6, pady=10, sticky="e")

        self.c_p_cpu_entry = ttk.Entry(self.frame_interior_3, validatecommand=float_positive_validator, validate='none')
        self.c_p_cpu_entry.grid(column=1, row=6, pady=10, sticky="ew", padx=10)

        # k: Thermal conductivity (W/m ºC)
        self.k_cpu_label = ttk.Label(self.frame_interior_3, text="Thermal conductivity (W/m ºC)")
        self.k_cpu_label.grid(column=0, row=7, pady=10, sticky="e")

        self.k_cpu_entry = ttk.Entry(self.frame_interior_3, validatecommand=float_positive_validator, validate='none')
        self.k_cpu_entry.grid(column=1, row=7, pady=10, sticky="ew", padx=10)

        #########################################
        # Separator
        self.sections_separator_3 = ttk.Separator(self, orient="vertical")
        self.sections_separator_3.grid(column=2, row=0, rowspan=2, padx=10, sticky="ns")
        #########################################

        # Frame to get elements near
        self.frame_interior_4 = ttk.Frame(self)
        self.frame_interior_4.grid(column=3, row=0, rowspan=2)

        # Origins location
        self.board_specification_label = ttk.Label(self.frame_interior_4,
                                                   text="CPU origins location (if not filled it will " +
                                                        "be generated automatically)")
        self.board_specification_label.grid(column=0, row=0, pady=10)

        self.origins_list = ttk.Treeview(self.frame_interior_4, columns=("y"))
        self.origins_list.grid(column=0, row=1, pady=10, sticky="ew", padx=10)

        self.origins_list.heading("#0", text="x(mm)")
        self.origins_list.heading("y", text="y(mm)")

        # Frame to get elements near
        self.frame_interior_5 = ttk.Frame(self.frame_interior_4)
        self.frame_interior_5.grid(column=0, row=2, pady=10, padx=10, sticky="e")

        # x
        self.x_label = ttk.Label(self.frame_interior_5, text="x: ")
        self.x_label.grid(column=0, row=0, pady=10, sticky="e")

        self.x_entry = ttk.Entry(self.frame_interior_5, validatecommand=float_positive_validator, validate='none')
        self.x_entry.grid(column=1, row=0, pady=10, sticky="ew", padx=10)

        # y
        self.y_label = ttk.Label(self.frame_interior_5, text="y: ")
        self.y_label.grid(column=0, row=1, pady=10, sticky="e")

        self.y_entry = ttk.Entry(self.frame_interior_5, validatecommand=float_positive_validator, validate='none')
        self.y_entry.grid(column=1, row=1, pady=10, sticky="ew", padx=10)

        # Add and delete task
        self.add_task_button = ttk.Button(self.frame_interior_5, text="Add",
                                          command=lambda: self.add_origin_callback(internal_error_handler))
        self.add_task_button.grid(column=1, row=2, pady=10, sticky="ew", padx=10)

        self.delete_task_button = ttk.Button(self.frame_interior_5, text="Delete selected",
                                             command=self.delete_origin_callback)
        self.delete_task_button.grid(column=1, row=3, pady=10, sticky="ew", padx=10)

    def add_origin_callback(self, internal_error_handler: Callable[[List[str]], None]):
        """
        Add the origin to the origins list if it is valid
        :param internal_error_handler: Error handler
        """
        # Check fields
        invalid_fields = []
        if not self.x_entry.validate():
            invalid_fields += ["Origin (x) coordinate"]
        if not self.y_entry.validate():
            invalid_fields += ["Origin (y) coordinate"]

        # Add task
        internal_error_handler(invalid_fields)

        if len(invalid_fields) == 0:
            self.origins_list.insert("", tk.END, text=self.x_entry.get(), values=(self.y_entry.get()))
            self.x_entry.delete(0, 'end')
            self.y_entry.delete(0, 'end')

    def delete_origin_callback(self):
        """
        Delete selected origin from the origins list
        """
        self.origins_list.delete(*self.origins_list.selection())

    def get_specification(self) -> CpuSpecification:
        """
        Get the specification if is valid, raise an exception otherwise
        :return: the specification
        """
        # Check fields
        invalid_fields = []
        if not self.m_entry.validate():
            invalid_fields += ["Number of CPU"]
        if not self.f_entry.validate():
            invalid_fields += ["Frequency"]

        if not self.x_board_entry.validate():
            invalid_fields += ["Board (x) coordinate"]
        if not self.y_board_entry.validate():
            invalid_fields += ["Board (y) coordinate"]
        if not self.z_board_entry.validate():
            invalid_fields += ["Board (z) coordinate"]
        if not self.c_p_board_entry.validate():
            invalid_fields += ["Board specific heat capacities"]
        if not self.p_board_entry.validate():
            invalid_fields += ["Board density"]
        if not self.k_board_entry.validate():
            invalid_fields += ["Board thermal conductivity"]

        if not self.x_cpu_entry.validate():
            invalid_fields += ["Cpu (x) coordinate"]
        if not self.y_cpu_entry.validate():
            invalid_fields += ["Cpu (y) coordinate"]
        if not self.z_cpu_entry.validate():
            invalid_fields += ["Cpu (z) coordinate"]
        if not self.c_p_cpu_entry.validate():
            invalid_fields += ["Cpu specific heat capacities"]
        if not self.p_cpu_entry.validate():
            invalid_fields += ["Cpu density"]
        if not self.k_cpu_entry.validate():
            invalid_fields += ["Cpu thermal conductivity"]

        if len(self.origins_list.get_children()) != 0 and len(self.origins_list.get_children()) != int(
                self.m_entry.get()):
            invalid_fields += ["Origins"]

        # Return
        if len(invalid_fields) > 0:
            raise InputValidationError(invalid_fields)
        else:
            m = int(self.m_entry.get())
            f = float(self.f_entry.get())

            board_x = float(self.x_board_entry.get())
            board_y = float(self.y_board_entry.get())
            board_z = float(self.z_board_entry.get())
            board_p = float(self.p_board_entry.get())
            board_c_p = float(self.c_p_board_entry.get())
            board_k = float(self.k_board_entry.get())
            board_material_cuboid = MaterialCuboid(board_x, board_y, board_z, board_p, board_c_p, board_k)

            cpu_x = float(self.x_cpu_entry.get())
            cpu_y = float(self.y_cpu_entry.get())
            cpu_z = float(self.z_cpu_entry.get())
            cpu_p = float(self.p_cpu_entry.get())
            cpu_c_p = float(self.c_p_cpu_entry.get())
            cpu_k = float(self.k_cpu_entry.get())
            cpu_material_cuboid = MaterialCuboid(cpu_x, cpu_y, cpu_z, cpu_p, cpu_c_p, cpu_k)

            origins = [
                Origin(float(self.origins_list.item(i).get("text")), float(self.origins_list.item(i).get("values")[0]))
                for i in self.origins_list.get_children()] if len(self.origins_list.get_children()) != 0 else None

            return CpuSpecification(board_material_cuboid, cpu_material_cuboid, m, f, origins)


class OutputControl(ttk.Frame):
    """
    Control of the scheduler specification input
    """

    def __init__(self, parent):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        # Frame to get elements near
        self.frame_interior = ttk.Frame(self)
        self.frame_interior.grid(column=0, row=0)

        self.combobox_values = ["Not display or save",
                                "Save in out folder",
                                "Display"]

        self.execution_and_task_allocation_label = ttk.Label(self.frame_interior,
                                                             text="Execution and task allocation: ")
        self.execution_and_task_allocation_label.grid(column=0, row=0, sticky="e", pady=10, padx=10)

        self.execution_and_task_allocation_combobox = ttk.Combobox(self.frame_interior, state="readonly")
        self.execution_and_task_allocation_combobox["values"] = self.combobox_values
        self.execution_and_task_allocation_combobox.grid(column=1, row=0, pady=10, sticky="ew", padx=10)

        self.thermal_evolution_label = ttk.Label(self.frame_interior,
                                                 text="Thermal evolution: ")
        self.thermal_evolution_label.grid(column=0, row=1, sticky="e", pady=10, padx=10)

        self.thermal_evolution_combobox = ttk.Combobox(self.frame_interior, state="readonly")
        self.thermal_evolution_combobox["values"] = self.combobox_values
        self.thermal_evolution_combobox.grid(column=1, row=1, pady=10, sticky="ew", padx=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    class OutputControlOptions(Enum):
        NOTHING = 0,
        SAVE = 1,
        PLOT = 2

    def get_specification(self) -> List[OutputControlOptions]:
        """
        Get the specification if is valid, raise an exception otherwise
        :return: the specification
        """
        # Scheduler definition name-id association
        combobox_values = {
            "Not display or save": self.OutputControlOptions.NOTHING,
            "Save in out folder": self.OutputControlOptions.SAVE,
            "Display": self.OutputControlOptions.PLOT
        }

        # Check fields
        invalid_fields = []
        if self.execution_and_task_allocation_combobox.get() == "" or self.thermal_evolution_combobox.get() == "":
            invalid_fields += ["Output"]
        elif self.execution_and_task_allocation_combobox.get() == "Not display or save" and \
                self.thermal_evolution_combobox.get() == "Not display or save":
            invalid_fields += ["Output, at least one must be displayed or saved"]
        # Return
        if len(invalid_fields) > 0:
            raise InputValidationError(invalid_fields)
        else:
            return [combobox_values.get(self.execution_and_task_allocation_combobox.get()),
                    combobox_values.get(self.thermal_evolution_combobox.get())]


class SpecificationCategoriesControl(ttk.Frame):
    def fields_error_handler(self, errors: List[str]):
        if len(errors) != 0:
            self.internal_message_handler("Error in fields: " + ', '.join(errors))
        else:
            self.internal_message_handler("Messages: Nothing running")

    def __init__(self, parent, internal_message_handler: Callable[[str], None]):
        super().__init__(parent)

        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(column=0, row=0, sticky="nsew")
        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.internal_message_handler = internal_message_handler

        # Creating each tab content
        self.tasks_specification_content = TaskSpecificationControl(self.notebook, self.fields_error_handler)
        self.tasks_specification_content.grid(column=0, row=0)
        self.notebook.add(self.tasks_specification_content, text="Tasks")

        self.cpu_specification_content = CpuSpecificationControl(self.notebook, self.fields_error_handler)
        self.cpu_specification_content.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
        self.notebook.add(self.cpu_specification_content, text="CPU")

        self.environment_content = EnvironmentSpecificationControl(self.notebook)
        self.environment_content.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
        self.notebook.add(self.environment_content, text="Environment")

        self.simulation_content = SimulationSpecificationControl(self.notebook)
        self.simulation_content.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
        self.notebook.add(self.simulation_content, text="Simulation")

        self.scheduler_content = SchedulerSpecificationControl(self.notebook)
        self.scheduler_content.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
        self.notebook.add(self.scheduler_content, text="Scheduler")

        self.output_content = OutputControl(self.notebook)
        self.output_content.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
        self.notebook.add(self.output_content, text="Output")


class GraphicalUserInterface(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Tabs panel
        self.tabs_panel = SpecificationCategoriesControl(self, self.message_show_handler)
        self.tabs_panel.grid(column=0, row=0, sticky="nsew")

        # Run simulation
        self.button_run_simulation = ttk.Button(self, text="Run simulation",
                                                command=lambda: threading.Thread(target=self.run_simulation).start())
        self.button_run_simulation.grid(column=0, row=1, pady=10)

        # Error label
        self.messages_label = ttk.Label(self, text="Messages: Nothing running")
        self.messages_label.grid(column=0, row=2)

        # Result stored
        self.simulation_result = None

    def message_show_handler(self, message: str):
        self.messages_label.config(text=message)

    def run_simulation(self):
        try:
            is_specification_with_thermal = True
            tasks_specification = self.tabs_panel.tasks_specification_content.get_specification()
            cpu_specification = self.tabs_panel.cpu_specification_content.get_specification()
            environment_specification = self.tabs_panel.environment_content.get_specification()
            simulation_specification = self.tabs_panel.simulation_content.get_specification()
            scheduler = self.tabs_panel.scheduler_content.get_specification()
            output_specification = self.tabs_panel.output_content.get_specification()

            self.message_show_handler("Wait: Simulation running")
            self.button_run_simulation.config(state="disabled")

            # Run the simulation
            processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

            tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

            thermal_model: Optional[ThermalModel] = generate_thermal_model(tasks_specification, cpu_specification,
                                                                           environment_specification,
                                                                           simulation_specification) if is_specification_with_thermal else None

            global_model, mo = generate_global_model(tasks_model, processor_model, thermal_model,
                                                     environment_specification)

            simulation_kernel: SimulationKernel = SimulationKernel(tasks_model, processor_model, thermal_model,
                                                                   global_model, mo)

            global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                            environment_specification,
                                                                            simulation_specification)

            try:
                simulation_result = scheduler.simulate(global_specification, simulation_kernel, None)

                p = Process(target=self.plot_output,
                            args=(global_specification, is_specification_with_thermal, output_specification,
                                  simulation_kernel, simulation_result)) # FIXME: That's a workaround
                p.start()

                self.message_show_handler("Simulation ended")
            except Exception as ex:
                self.message_show_handler("Error: " + ex.args[0])
            self.button_run_simulation.config(state="normal")

        except InputValidationError as ve:
            self.message_show_handler("Error in fields: " + ', '.join(ve.args[0]))

    def plot_output(self, global_specification, is_specification_with_thermal, output_specification, simulation_kernel,
                    simulation_result):
        output_path = "out/"
        output_base_name = "simulation"
        # Create output directory if not exist
        os.makedirs(output_path, exist_ok=True)
        if output_specification[0] == OutputControl.OutputControlOptions.SAVE:
            plot_cpu_utilization(global_specification, simulation_result,
                                 os.path.join(output_path, output_base_name + "_cpu_utilization.png"))
            plot_task_execution(global_specification, simulation_result,
                                os.path.join(output_path, output_base_name + "_task_execution.png"))
            plot_accumulated_execution_time(global_specification, simulation_result,
                                            os.path.join(output_path,
                                                         output_base_name + "_accumulated_execution_time.png"))
            if is_specification_with_thermal:
                plot_cpu_temperature(global_specification, simulation_result,
                                     os.path.join(output_path, output_base_name + "_cpu_temperature.png"))

        elif output_specification[0] == OutputControl.OutputControlOptions.PLOT:
            plot_cpu_utilization(global_specification, simulation_result)
            plot_task_execution(global_specification, simulation_result)
            plot_accumulated_execution_time(global_specification, simulation_result)
            if is_specification_with_thermal:
                plot_cpu_temperature(global_specification, simulation_result)
        if output_specification[1] == OutputControl.OutputControlOptions.SAVE:
            draw_heat_matrix(global_specification, simulation_kernel, simulation_result,
                             os.path.join(output_path, output_base_name + "heat_matrix.mp4"))
        elif output_specification[1] == OutputControl.OutputControlOptions.PLOT:
            draw_heat_matrix(global_specification, simulation_kernel, simulation_result)


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Scheduler simulation Framework")
    gui = GraphicalUserInterface(window)
    gui.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    window.mainloop()
