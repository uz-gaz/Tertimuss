import tkinter as tk
import tkinter.ttk as ttk
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


# TODO: Do no thermal gui, position elements correctly and improve visual

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

    def __init__(self, parent, internal_error_handler: Callable[[List[str]], None]):
        """
        :param parent: The parent window
        """
        super().__init__(parent)

        # Validators
        float_positive_validator = (self.register(lambda x: Validators.is_float_validator(x, 0)), '%P')
        integer_positive_validator = (self.register(lambda x: Validators.is_integer_validator(x, 0)), '%P')

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

        self.c_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.c_entry.grid(column=1, row=4)

        # t: Task period, equal to deadline
        self.t_label = ttk.Label(self, text="Task period, equal to deadline: ")
        self.t_label.grid(column=0, row=5)

        self.t_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.t_entry.grid(column=1, row=5)

        # e: Energy consumption
        self.e_label = ttk.Label(self, text="Energy consumption: ")
        self.e_label.grid(column=0, row=6)

        self.e_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.e_entry.grid(column=1, row=6)

        # Add and delete task
        self.delete_task_button = ttk.Button(self, text="Delete selected",
                                             command=self.delete_task_callback)
        self.delete_task_button.grid(column=0, row=7)

        self.add_task_button = ttk.Button(self, text="Add",
                                          command=lambda: self.add_task_callback(internal_error_handler))
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

        self.number_of_task_entry = ttk.Entry(self, validatecommand=integer_positive_validator, validate='none')
        self.number_of_task_entry.grid(column=4, row=2)

        # Utilization
        self.utilization_label = ttk.Label(self, text="Utilization: ")
        self.utilization_label.grid(column=3, row=3)

        self.utilization_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.utilization_entry.grid(column=4, row=3)

        # Interval for periods
        self.interval_for_periods_label = ttk.Label(self, text="Interval for periods: ")
        self.interval_for_periods_label.grid(column=3, row=4)

        self.interval_for_periods_start_entry = ttk.Entry(self, validatecommand=float_positive_validator,
                                                          validate='none')
        self.interval_for_periods_start_entry.grid(column=4, row=4)

        self.interval_for_periods_end_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.interval_for_periods_end_entry.grid(column=5, row=4)

        # Generate
        self.generate_button = ttk.Button(self, text="Generate",
                                          command=lambda: self.generate_automatic_tasks(internal_error_handler))
        self.generate_button.grid(column=5, row=5)

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
        if len(invalid_fields) > 0:
            internal_error_handler(invalid_fields)
        else:
            self.tasks_list.insert("", tk.END, text=self.c_entry.get(), values=(self.t_entry.get(), self.e_entry.get()))

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

        # m: Number of CPU
        self.m_label = ttk.Label(self, text="Number of CPU: ")
        self.m_label.grid(column=0, row=0)

        self.m_entry = ttk.Entry(self, validatecommand=integer_positive_validator, validate='none')
        self.m_entry.grid(column=1, row=0)

        # f: Frequency
        self.f_label = ttk.Label(self, text="Frequency: ")
        self.f_label.grid(column=0, row=1)

        self.f_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
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

        self.x_board_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.x_board_entry.grid(column=4, row=1)
        # y(mm)
        self.y_board_label = ttk.Label(self, text="y(mm)")
        self.y_board_label.grid(column=3, row=2)

        self.y_board_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.y_board_entry.grid(column=4, row=2)

        # z(mm)
        self.z_board_label = ttk.Label(self, text="z(mm)")
        self.z_board_label.grid(column=3, row=3)

        self.z_board_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.z_board_entry.grid(column=4, row=3)

        # p: Density (Kg/cm^3)
        self.p_board_label = ttk.Label(self, text="Density (Kg/cm^3)")
        self.p_board_label.grid(column=3, row=4)

        self.p_board_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.p_board_entry.grid(column=4, row=4)

        # c_p: Specific heat capacities (J/Kg K)
        self.c_p_board_label = ttk.Label(self, text="Specific heat capacities (J/Kg K)")
        self.c_p_board_label.grid(column=3, row=5)

        self.c_p_board_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.c_p_board_entry.grid(column=4, row=5)

        # k: Thermal conductivity (W/m ºC)
        self.k_board_label = ttk.Label(self, text="Thermal conductivity (W/m ºC)")
        self.k_board_label.grid(column=3, row=6)

        self.k_board_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
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

        self.x_cpu_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.x_cpu_entry.grid(column=4, row=9)
        # y(mm)
        self.y_cpu_label = ttk.Label(self, text="y(mm)")
        self.y_cpu_label.grid(column=3, row=10)

        self.y_cpu_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.y_cpu_entry.grid(column=4, row=10)

        # z(mm)
        self.z_cpu_label = ttk.Label(self, text="z(mm)")
        self.z_cpu_label.grid(column=3, row=11)

        self.z_cpu_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.z_cpu_entry.grid(column=4, row=11)

        # p: Density (Kg/cm^3)
        self.p_cpu_label = ttk.Label(self, text="Density (Kg/cm^3)")
        self.p_cpu_label.grid(column=3, row=12)

        self.p_cpu_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.p_cpu_entry.grid(column=4, row=12)

        # c_p: Specific heat capacities (J/Kg K)
        self.c_p_cpu_label = ttk.Label(self, text="Specific heat capacities (J/Kg K)")
        self.c_p_cpu_label.grid(column=3, row=13)

        self.c_p_cpu_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.c_p_cpu_entry.grid(column=4, row=13)

        # k: Thermal conductivity (W/m ºC)
        self.k_cpu_label = ttk.Label(self, text="Thermal conductivity (W/m ºC)")
        self.k_cpu_label.grid(column=3, row=14)

        self.k_cpu_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.k_cpu_entry.grid(column=4, row=14)

        #########################################
        # Separator
        self.sections_separator_3 = ttk.Separator(self, orient="vertical")
        self.sections_separator_3.grid(column=5, row=7, rowspan=8, sticky="ns")
        #########################################

        # Origins location
        self.board_specification_label = ttk.Label(self,
                                                   text="CPU origins location (if not filled it will " +
                                                        "be generated automatically)")
        self.board_specification_label.grid(column=6, row=8)

        self.origins_list = ttk.Treeview(self, columns=("y"))
        self.origins_list.grid(column=6, row=9, columnspan=2, rowspan=4)

        self.origins_list.heading("#0", text="x(mm)")
        self.origins_list.heading("y", text="y(mm)")

        # x
        self.x_label = ttk.Label(self, text="x: ")
        self.x_label.grid(column=6, row=14)

        self.x_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.x_entry.grid(column=7, row=14)

        # y
        self.y_label = ttk.Label(self, text="y: ")
        self.y_label.grid(column=6, row=15)

        self.y_entry = ttk.Entry(self, validatecommand=float_positive_validator, validate='none')
        self.y_entry.grid(column=7, row=15)

        # Add and delete task
        self.delete_task_button = ttk.Button(self, text="Delete selected", command=self.delete_origin_callback)
        self.delete_task_button.grid(column=6, row=16)

        self.add_task_button = ttk.Button(self, text="Add",
                                          command=lambda: self.add_origin_callback(internal_error_handler))
        self.add_task_button.grid(column=7, row=16)

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
        if len(invalid_fields) > 0:
            internal_error_handler(invalid_fields)
        else:
            self.origins_list.insert("", tk.END, text=self.x_entry.get(), values=(self.y_entry.get()))

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


class SpecificationCategoriesControl(ttk.Frame):
    def __init__(self, parent, internal_error_handler: Callable[[List[str]], None]):
        super().__init__(parent)

        self.notebook = ttk.Notebook(parent)
        self.notebook.place(x=0, y=0)
        self.place(relwidth=1, relheight=1)

        # Creating each tab content
        self.environment_content = EnvironmentSpecificationControl(self.notebook)
        self.environment_content.place(relwidth=1, relheight=1)

        self.simulation_content = SimulationSpecificationControl(self.notebook)
        self.simulation_content.place(relwidth=1, relheight=1)

        self.scheduler_content = SchedulerSpecificationControl(self.notebook)
        self.scheduler_content.place(relwidth=1, relheight=1)

        self.tasks_specification_content = TaskSpecificationControl(self.notebook, internal_error_handler)
        self.tasks_specification_content.place(relwidth=1, relheight=1)

        self.cpu_specification_content = CpuSpecificationControl(self.notebook, internal_error_handler)
        self.cpu_specification_content.place(relwidth=1, relheight=1)

        # Add tab with text
        self.notebook.add(self.tasks_specification_content, text="Tasks")
        self.notebook.add(self.cpu_specification_content, text="CPU")
        self.notebook.add(self.environment_content, text="Environment")
        self.notebook.add(self.simulation_content, text="Simulation")
        self.notebook.add(self.scheduler_content, text="Scheduler")


class GraphicalUserInterface(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        def error_handler(errors: List[str]):
            # TODO: Improve errors
            print("Fields: " + ', '.join(errors))

        gui = SpecificationCategoriesControl(window, error_handler)
        gui.place(x=0, y=0)

        self.simulation_result = None

        def run_simulation():
            try:
                is_specification_with_thermal = False
                tasks_specification = gui.tasks_specification_content.get_specification()
                cpu_specification = gui.cpu_specification_content.get_specification()
                environment_specification = gui.environment_content.get_specification()
                simulation_specification = gui.simulation_content.get_specification()
                scheduler = gui.scheduler_content.get_specification()

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
                    self.simulation_result = scheduler.simulate(global_specification, simulation_kernel, None)
                except Exception as ex:
                    print(ex)
                    return 1

            except InputValidationError as ve:
                error_handler(ve.args[0])

        # TODO: Disable button while simulation is running, and show progress in progressbar
        # TODO: Add tab to show output
        button_calc = tk.Button(self, text="Run simulation", command=run_simulation)
        button_calc.place(x=1000, y=500)


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Scheduler simulation Framework")
    window.configure(width=1200, height=700)
    gui = GraphicalUserInterface(window)
    window.mainloop()
