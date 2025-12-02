#!/usr/bin/env python3
"""
NFL Parlay Generator - Windows Launcher
Runs without console window (uses pythonw.exe)
"""

import sys
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import and run the GUI
try:
    from NFL_GUI import main
    main()
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "NFL Parlay Generator Error",
        f"Failed to start:\n\n{str(e)}\n\nMake sure all dependencies are installed:\npip install pydantic rich requests pytz"
    )
    sys.exit(1)
