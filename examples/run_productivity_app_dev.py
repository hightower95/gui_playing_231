"""
Run Productivity App in Development Mode

This script starts the productivity app with a separate configuration directory
for development purposes. Useful for running dev and live versions side-by-side.

Usage:
    python run_productivity_app_dev.py  # Runs with app_name='productivity_app_dev'
"""
import productivity_app

if __name__ == "__main__":
    # Run with dev configuration directory
    # This will use: C:/Users/{user}/AppData/Roaming/SwissArmyTool/productivity_app_dev
    productivity_app.start(app_name='productivity_app_dev')
