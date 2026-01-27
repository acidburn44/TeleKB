import tkinter as tk
from tkinter import messagebox
import sys
import os
from TeleKB.config import Config
from TeleKB.gui.main_window import MainWindow

def main():
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        # We can't use tk message box easily if root not created yet, 
        # but let's create a temporary root to show error.
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Configuration Error", str(e) + "\n\nPlease ensure you have a .env file with API_ID, API_HASH, and GEMINI_API_KEY.")
        return

    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
