import tkinter as tk
from dashboard import Dashboard

if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_update)
    root.mainloop()