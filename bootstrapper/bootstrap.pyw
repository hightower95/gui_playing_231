"""
Bootstrap Wizard Launcher (No Console)
Run this file to launch the wizard without a console window
"""
import bootstrap

if __name__ == "__main__":
    try:
        app = bootstrap.SetupWizard()
        app.mainloop()
    except Exception as e:
        import traceback
        from pathlib import Path
        
        # Log errors to file since we have no console
        error_log = Path(__file__).parent / "logs" / "error.log"
        error_log.parent.mkdir(exist_ok=True)
        
        with open(error_log, 'w') as f:
            f.write(f"Error starting wizard: {e}\n")
            traceback.print_exc(file=f)
