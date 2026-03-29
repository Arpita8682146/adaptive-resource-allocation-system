import tkinter as tk
from tkinter import ttk
import psutil
from monitor import monitor, cpu_data, mem_data
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Resource Dashboard")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e2f")

        # Progress Bars
        self.cpu_bar = ttk.Progressbar(root, length=300)
        self.cpu_bar.pack(pady=10)

        self.mem_bar = ttk.Progressbar(root, length=300)
        self.mem_bar.pack(pady=10)

        # Process List
        self.box = tk.Text(root, height=10)
        self.box.pack(fill="x")

        # Graph
        self.fig, (self.ax1, self.ax2) = plt.subplots(2,1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.update()

    def update(self):
        cpu, mem = monitor()

        self.cpu_bar['value'] = cpu
        self.mem_bar['value'] = mem

        self.box.delete('1.0', tk.END)

        for proc in psutil.process_iter(['pid','name','cpu_percent']):
            try:
                self.box.insert(tk.END, f"{proc.info['pid']} | {proc.info['name']} | {proc.info['cpu_percent']}%\n")
            except:
                pass

        self.ax1.clear()
        self.ax1.plot(cpu_data)
        self.ax1.set_title("CPU")

        self.ax2.clear()
        self.ax2.plot(mem_data)
        self.ax2.set_title("Memory")

        self.canvas.draw()

        self.root.after(2000, self.update)