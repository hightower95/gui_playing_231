"""
Bootstrap Wizard Launcher - Direct launcher for development
Run this file directly from VS Code when working in the productivity_app_installer directory
"""
from bootstrap import SetupWizard
import sys
from pathlib import Path

# Add installer directory to Python path for direct execution
installer_dir = Path(__file__).parent / "installer"
sys.path.insert(0, str(installer_dir))

# Import and run

if __name__ == "__main__":
    try:
        app = SetupWizard()
        app.mainloop()
    except Exception as e:
        import traceback
        from pathlib import Path

        # Log errors to file since we have no console
        error_log = Path(__file__).parent / "installer" / "logs" / "error.log"
        error_log.parent.mkdir(exist_ok=True)

        with open(error_log, 'w') as f:
            f.write(f"Error starting wizard from bootstrap.pyw: {e}\n")
            traceback.print_exc(file=f)

        # Also try to show error in console for development
        print(f"Error starting wizard: {e}")
        traceback.print_exc()
