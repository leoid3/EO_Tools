# ---------------------------------------------------------------
# Creation of a GUI for the creation of a Traffic Model
#
# (C) 2024 César Leal-Graciani Mena, Toulouse, France
# email leal@satconsult.eu
# ---------------------------------------------------------------

import tkinter as tk
from TrafficModelClasses import MapApplication, TerminalDistribution
import traceback


def main():
    try:
        root = tk.Tk()
        root.title("Traffic_Model")
        root.geometry("1500x800")
        #root.attributes('-fullscreen', True)

        # Dependency injection application
        map_app = MapApplication(root)
        terminal = TerminalDistribution(map_app)
        map_app.set_terminal_distribution(terminal)

        root.mainloop()
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write("An error occurred:\n")
            f.write(traceback.format_exc())
        input("An error occurred. Press Enter to exit.")


if __name__ == "__main__":
    main()
