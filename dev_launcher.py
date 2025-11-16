#!/usr/bin/env python3
"""
Development Launcher - Quick access to different app modes
"""
import sys
import subprocess
from pathlib import Path


def run_main_gui():
    """Run the standalone main.py GUI"""
    print("🚀 Starting development GUI (main.py)...")
    subprocess.run([sys.executable, "main.py"])


def run_productivity_app():
    """Run the packaged productivity app"""
    print("📦 Starting packaged productivity app...")
    subprocess.run(
        [sys.executable, "-c", "import productivity_app; productivity_app.start()"])


def run_from_examples():
    """Run from examples directory"""
    print("📁 Starting from examples...")
    subprocess.run([sys.executable, "examples/run_productivity_app.py"])


def show_menu():
    """Show launcher menu"""
    print("\n" + "="*50)
    print("🛠️  DEVELOPMENT LAUNCHER")
    print("="*50)
    print("1. Development GUI (main.py)")
    print("2. Packaged Productivity App")
    print("3. Examples Launcher")
    print("4. Exit")
    print("="*50)

    choice = input("Select option (1-4): ").strip()

    if choice == "1":
        run_main_gui()
    elif choice == "2":
        run_productivity_app()
    elif choice == "3":
        run_from_examples()
    elif choice == "4":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please try again.")
        show_menu()


if __name__ == "__main__":
    # Change to the gui directory
    gui_dir = Path(__file__).parent
    import os
    os.chdir(gui_dir)

    # Show menu if no arguments, otherwise run directly
    if len(sys.argv) > 1:
        if sys.argv[1] == "main":
            run_main_gui()
        elif sys.argv[1] == "app":
            run_productivity_app()
        elif sys.argv[1] == "examples":
            run_from_examples()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Available: main, app, examples")
    else:
        show_menu()
