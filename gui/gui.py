import tkinter as tk
import tkinter.ttk as ttk


class EnvironmentSpecificationControl(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.h = ttk.Label(self, text="Hola, mundo!")
        self.h.grid(column=0, row=0)


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
    window.configure(width=700, height=700)
    gui = EnvironmentSpecificationControl(window)
    gui.place(relwidth=1, relheight=1)
    gui.mainloop()