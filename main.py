#!/usr/bin/env python3
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
