"""
My Application About / Help
Opens the help page in the default web browser
"""
import webbrowser
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        # Open help page in default browser
        webbrowser.open("https://example.com/help")
    except Exception as e:
        # Show error if browser fails to open
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to open help page: {e}")

if __name__ == "__main__":
    main()
