"""
Development launcher script for Productivity App.

Run this script during development to launch the application.
"""
import productivity_app
import sys
import os

# Add current directory to path so productivity_app can be imported
sys.path.insert(0, os.path.dirname(__file__))


if __name__ == "__main__":
    productivity_app.start()
