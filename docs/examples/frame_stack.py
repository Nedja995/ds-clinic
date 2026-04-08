import tkinter as tk
from tkinter import ttk

class FrameStack(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.subframes = []
        self.topFrame = tk.Frame(self)
        self.groupOfFrames = tk.Frame(self, height=200)
        self.topFrame.pack(side="top", fill="x")
        self.groupOfFrames.pack(side="top", fill="both", expand=True)

        self.add = tk.Button(self.topFrame, text="+", command=self.add_frame)
        self.add.pack(side="right")

    def delete_frame(self, frame):
        self.subframes.remove(frame)
        frame.destroy()

    def add_frame(self):
        f = SubFrame(parent=self.groupOfFrames, controller=self)
        self.subframes.append(f)
        f.pack(side="top", fill="x")

class SubFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.cb = ttk.Combobox(self)
        self.entry = tk.Entry(self)
        self.main_button = tk.Button(self, width=10)
        self.remove_button = tk.Button(self, text="-", command=self.remove)

        self.grid_rowconfigure(0, weight=1)
        self.cb.grid(row=0, column=0, sticky="ew")
        self.entry.grid(row=1, column=0, sticky="ew")
        self.main_button.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.remove_button.grid(row=1, column=2, sticky="se")

    def remove(self):
        self.controller.delete_frame(self)

root = tk.Tk()
root.geometry("400x400")

fs = FrameStack(root)
fs.pack(fill="both", expand=True)
root.mainloop()