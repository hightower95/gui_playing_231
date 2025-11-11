#!/usr/bin/env python3

"""
Test script to verify enable_folder_selection setting functionality
"""

import configparser
from install_gui.steps.folder_step import GetFolderStep
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
import sys
from pathlib import Path

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))


def create_test_config(enable_selection=True):
    """Create test configuration with enable_folder_selection setting"""
    config = configparser.ConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'app_name', 'TestApp')

    config.add_section('Step_Select_Folder')
    config.set('Step_Select_Folder',
               'lock_install_to_local_hard_drive', 'true')
    config.set('Step_Select_Folder', 'hard_drive_letter_restrictions', '["C"]')
    config.set('Step_Select_Folder', 'default_installation_folder',
               '["{parent_folder}"]')
    config.set('Step_Select_Folder', 'fallback_installation_folders',
               '["C:\\Program Files"]')
    config.set('Step_Select_Folder', 'enable_folder_selection',
               str(enable_selection).lower())

    return config


def test_enable_folder_selection():
    """Test both enabled and disabled folder selection"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create main window
    window = QWidget()
    window.setWindowTitle("Test enable_folder_selection Setting")
    window.setGeometry(100, 100, 800, 600)

    layout = QVBoxLayout()
    window.setLayout(layout)

    # Instructions
    instructions = QLabel("""
ENABLE_FOLDER_SELECTION TEST

This test shows both ENABLED and DISABLED folder selection modes.

ENABLED mode (top):
- Browse button should be enabled
- Path input should be editable
- Hint text: "Click browse button to change..."

DISABLED mode (bottom):
- Browse button should be disabled with tooltip
- Path input should be read-only (grayed out)
- Hint text: "Installation folder has been pre-configured..."
""")
    instructions.setWordWrap(True)
    layout.addWidget(instructions)

    # Test 1: ENABLED folder selection
    enabled_label = QLabel("=== ENABLED FOLDER SELECTION ===")
    enabled_label.setStyleSheet(
        "font-weight: bold; color: green; margin-top: 20px;")
    layout.addWidget(enabled_label)

    config_enabled = create_test_config(enable_selection=True)
    shared_state_enabled = {}

    folder_step_enabled = GetFolderStep(config_enabled, shared_state_enabled)
    folder_step_enabled.create_widgets(window, layout)

    # Add separator
    separator1 = QLabel("─" * 50)
    separator1.setStyleSheet("color: #ccc; margin: 20px 0;")
    layout.addWidget(separator1)

    # Test 2: DISABLED folder selection
    disabled_label = QLabel("=== DISABLED FOLDER SELECTION ===")
    disabled_label.setStyleSheet(
        "font-weight: bold; color: red; margin-top: 20px;")
    layout.addWidget(disabled_label)

    config_disabled = create_test_config(enable_selection=False)
    shared_state_disabled = {}

    folder_step_disabled = GetFolderStep(
        config_disabled, shared_state_disabled)
    folder_step_disabled.create_widgets(window, layout)

    # Add test buttons
    separator2 = QLabel("─" * 50)
    separator2.setStyleSheet("color: #ccc; margin: 20px 0;")
    layout.addWidget(separator2)

    test_label = QLabel("TEST FUNCTIONALITY:")
    test_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(test_label)

    def test_enabled_browse():
        print("\n=== Testing ENABLED Browse Button ===")
        print(
            f"Button enabled: {folder_step_enabled.browse_button.isEnabled()}")
        print(
            f"Input read-only: {folder_step_enabled.path_input.isReadOnly()}")
        print(f"Hint text: {folder_step_enabled.get_hint_text()}")
        folder_step_enabled._browse_for_folder()

    def test_disabled_browse():
        print("\n=== Testing DISABLED Browse Button ===")
        print(
            f"Button enabled: {folder_step_disabled.browse_button.isEnabled()}")
        print(
            f"Input read-only: {folder_step_disabled.path_input.isReadOnly()}")
        print(f"Hint text: {folder_step_disabled.get_hint_text()}")
        print(
            f"Button tooltip: {folder_step_disabled.browse_button.toolTip()}")
        folder_step_disabled._browse_for_folder()

    test_enabled_btn = QPushButton("Test ENABLED Browse (should open dialog)")
    test_enabled_btn.clicked.connect(test_enabled_browse)
    layout.addWidget(test_enabled_btn)

    test_disabled_btn = QPushButton(
        "Test DISABLED Browse (should show info message)")
    test_disabled_btn.clicked.connect(test_disabled_browse)
    layout.addWidget(test_disabled_btn)

    window.show()

    print("=== FOLDER SELECTION TEST LAUNCHED ===")
    print("Check the following:")
    print("1. ENABLED section: Browse button enabled, input editable")
    print("2. DISABLED section: Browse button disabled, input read-only/grayed")
    print("3. Different hint texts between sections")
    print("4. Click test buttons to verify behavior")

    app.exec()


if __name__ == "__main__":
    test_enable_folder_selection()
