#!/usr/bin/env python3
"""
Test script to verify GUI components functionality
"""
from install_gui.gui_components import (
    StatusTypes, StatusColors, ButtonLabels, DialogTitles_step_folder,
    get_status_color, get_status_message, apply_status_styling
)
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))


def test_gui_components():
    """Test GUI components and constants"""
    print("Testing GUI Components")
    print("=" * 50)

    # Test status colors
    print("Status Colors:")
    print(f"  SUCCESS: {get_status_color(StatusTypes.SUCCESS)}")
    print(f"  ERROR: {get_status_color(StatusTypes.ERROR)}")
    print(f"  INFO: {get_status_color(StatusTypes.INFO)}")
    print(f"  DEFAULT: {get_status_color(StatusTypes.DEFAULT)}")

    # Test status messages
    print("\nDefault Status Messages:")
    print(f"  GREEN: {get_status_message(StatusTypes.GREEN)}")
    print(f"  RED: {get_status_message(StatusTypes.RED)}")
    print(f"  GREY: {get_status_message(StatusTypes.GREY)}")

    # Test custom messages
    print("\nCustom Messages:")
    print(
        f"  GREEN with custom: {get_status_message(StatusTypes.GREEN, 'Custom success message')}")

    # Test constants
    print("\nButton Labels:")
    print(f"  BROWSE: {ButtonLabels.BROWSE}")
    print(f"  COMPLETE_STEP: {ButtonLabels.COMPLETE_STEP}")

    print("\nDialog Titles:")
    print(f"  SELECT_FOLDER: {DialogTitles_step_folder.SELECT_FOLDER}")
    print(f"  INVALID_PATH: {DialogTitles_step_folder.INVALID_PATH}")

    # Test color constants directly
    print("\nDirect Color Constants:")
    print(f"  SUCCESS: {StatusColors.SUCCESS}")
    print(f"  ERROR: {StatusColors.ERROR}")
    print(f"  INFO: {StatusColors.INFO}")

    print("\nAll tests completed successfully!")


if __name__ == "__main__":
    test_gui_components()
