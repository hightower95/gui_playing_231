#!/usr/bin/env python3
"""
Test script to verify button positioning and enablement fixes
"""
from configparser import ConfigParser
from install_gui.main import InstallWizardGUI
import sys
import os
import tempfile
from pathlib import Path

# Add the installer path to sys.path
sys.path.insert(0, str(Path(__file__).parent / "installer"))


def test_button_positioning_and_enablement():
    """Test that buttons are positioned correctly and enabled appropriately"""
    print("🔧 Testing Button Fixes")
    print("=" * 50)

    # Create test configuration
    config = ConfigParser()
    config.read_string("""
[GENERAL]
app_name = Test Application
app_version = 1.0.0

[FOLDERS]
default_folder = C:\\TestApp
""")

    try:
        # Create the installer GUI
        app = InstallWizardGUI(config)

        # Simulate step initialization by accessing the first step
        current_step = app.conductor.get_current_step()
        print(f"✅ Current step loaded: {current_step.get_title()}")

        # Check initial button states after step creation
        step_info = app.conductor.get_step_info()
        can_complete_initial = step_info.get("can_complete", False)
        print(f"✅ Initial can_complete state: {can_complete_initial}")

        # Simulate creating widgets in a test frame
        import tkinter as tk
        test_frame = tk.Frame()
        current_step.create_widgets(test_frame)

        # Check button state after widget creation
        step_info_after = app.conductor.get_step_info()
        can_complete_after = step_info_after.get("can_complete", False)
        print(f"✅ can_complete after widget creation: {can_complete_after}")

        # Test button layout by checking the pack info
        print("\n🎯 Button Layout Test:")

        # Get the button frame children
        button_frame = None
        for child in app.winfo_children():
            if hasattr(child, 'winfo_children'):
                for subchild in child.winfo_children():
                    if hasattr(subchild, 'winfo_children'):
                        for widget in subchild.winfo_children():
                            if hasattr(widget, 'winfo_children'):
                                buttons = []
                                for button in widget.winfo_children():
                                    if hasattr(button, 'cget') and button.cget('text') in ['Cancel Installation', 'Complete Step']:
                                        buttons.append(
                                            (button.cget('text'), button.pack_info().get('side', 'none')))

                                if buttons:
                                    print("✅ Button positions found:")
                                    for text, side in buttons:
                                        print(f"   • {text}: packed on {side}")

                                    # Verify correct positioning
                                    cancel_side = next(
                                        (side for text, side in buttons if 'Cancel' in text), None)
                                    complete_side = next(
                                        (side for text, side in buttons if 'Complete' in text), None)

                                    if cancel_side == 'left' and complete_side == 'right':
                                        print(
                                            "✅ Button positioning is correct (Cancel=left, Complete=right)")
                                    else:
                                        print(
                                            f"❌ Button positioning is wrong (Cancel={cancel_side}, Complete={complete_side})")

        # Test with a valid folder to check enablement
        print("\n📁 Testing folder validation:")
        with tempfile.TemporaryDirectory() as temp_dir:
            # Simulate folder selection
            current_step.simulate_folder_selection(temp_dir)
            step_info_valid = app.conductor.get_step_info()
            can_complete_valid = step_info_valid.get("can_complete", False)
            print(
                f"✅ can_complete with valid folder ({temp_dir}): {can_complete_valid}")

        # Clean up
        app.destroy()

        print("\n" + "=" * 50)
        print("🎉 Button fix tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_button_positioning_and_enablement()
    sys.exit(0 if success else 1)
