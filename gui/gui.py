import tkinter as tk
import tkinter.ttk as ttk

from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification


class EnvironmentSpecificationControl(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # h: Convection factor (W/mm^2 ºC)
        self.h_label = ttk.Label(self, text="Convection factor (W/mm^2 ºC): ")
        self.h_label.grid(column=0, row=0)

        self.h_entry = ttk.Entry(self)
        self.h_entry.grid(column=1, row=0)

        # t_env: Environment temperature (ºC)
        self.t_env_label = ttk.Label(self, text="Environment temperature (ºC): ")
        self.t_env_label.grid(column=0, row=1)

        self.t_env_entry = ttk.Entry(self)
        self.t_env_entry.grid(column=1, row=1)

        # t_max: Maximum temperature (ºC)
        self.t_max_label = ttk.Label(self, text="Maximum temperature (ºC): ")
        self.t_max_label.grid(column=0, row=2)

        self.t_max_entry = ttk.Entry(self)
        self.t_max_entry.grid(column=1, row=2)

    def get_specification(self):
        # TODO: Validate input and get correct type
        h: float = self.h_entry.get()
        t_max: float = self.t_max_entry.get()
        t_env: float = self.t_env_entry.get()
        return EnvironmentSpecification(h, t_env, t_max)


class SimulationSpecificationControl(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # step: Mesh step size (mm)
        self.step_label = ttk.Label(self, text="Mesh step size (mm): ")
        self.step_label.grid(column=0, row=0)

        self.step_entry = ttk.Entry(self)
        self.step_entry.grid(column=1, row=0)

        # dt:  Accuracy (s)
        self.dt_label = ttk.Label(self, text="Accuracy (s): ")
        self.dt_label.grid(column=0, row=1)

        self.dt_entry = ttk.Entry(self)
        self.dt_entry.grid(column=1, row=1)


class TaskSpecificationControl(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Task list
        self.tasks_list = ttk.Treeview(self, columns=("t", "e"))
        self.tasks_list.grid(column=0, row=0, columnspan=2, rowspan = 4)
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


class SpecificationCategoriesControl(ttk.Frame):
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
    def __init__(self, parent):
        super().__init__(parent)
        self.place(relwidth=1, relheight=1)
        self.task_specification = EnvironmentSpecificationControl(self)


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Scheduler simulation Framework")
    window.configure(width=1200, height=700)
    gui = TaskSpecificationControl(window)
    gui.place(relwidth=1, relheight=1)
    # gui.grid(column=0, row=0)
    # button_calc = tk.Button(window, text="Calculate", command=lambda: print(gui.get_specification().h))
    # button_calc.grid(column=0, row=1)
    window.mainloop()
