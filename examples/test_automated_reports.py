"""
Demo script for Automated Reports experiment

Run this to test the new automated reports feature.
"""
from productivity_app.productivity_core.tabs.automated_reports import AutomatedReportsView
from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Launch the automated reports demo"""
    app = QApplication(sys.argv)

    # Create and show the view
    window = AutomatedReportsView()
    window.setWindowTitle("Automated Reports - Experiment")
    window.resize(1400, 800)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
