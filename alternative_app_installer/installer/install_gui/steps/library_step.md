# Library Step Documentation

## Process Flow

```
┌─────────────────────┐    ┌──────────────────────┐    ┌────────────────────┐
│   create_widgets()  │───▶│ _load_configuration()│───▶│ _create_checklist()│
└─────────────────────┘    └──────────────────────┘    └────────────────────┘
           │                                                        │
           ▼                                                        ▼
┌─────────────────────┐    ┌──────────────────────────────────────────────────┐
│ _populate_initial_  │◀───┤           CHECKLIST UI                          │
│   checklist()       │    │  1. Version (stable/latest)                     │
└─────────────────────┘    │  2. Index-url source                            │
           │                │  3. Install status                              │
           ▼                │  4. Verification                                │
┌─────────────────────┐    └──────────────────────────────────────────────────┘
│get_latest_stable_   │                           │
│  version()          │                           ▼
└─────────────────────┘    ┌──────────────────────────────────────────────────┐
                           │              [Install Libraries]                 │
                           └──────────────────────┬───────────────────────────┘
                                                  │
                           ┌──────────────────────▼───────────────────────────┐
                           │        _start_library_installation()             │
                           └──────────────────────┬───────────────────────────┘
                                                  │
                           ┌──────────────────────▼───────────────────────────┐
                           │       LibraryInstallationWorker.run()            │
                           │                                                  │
                           │  cmd = [venv_python, "-m", "pip", "install",    │
                           │         "--report", "report.json", libraries]    │
                           └──────────────────────┬───────────────────────────┘
                                                  │
                           ┌──────────────────────▼───────────────────────────┐
                           │             _check_queues()                      │
                           └──────────────────────┬───────────────────────────┘
                                                  │
                           ┌──────────────────────▼───────────────────────────┐
                           │           _verify_installation()                 │
                           │                                                  │
                           │  pip show <library>                              │
                           │  _parse_install_report(report_path)              │
                           └──────────────────────────────────────────────────┘
```

## Configuration Parameters

**Section:** `[Step_Install_Libraries]`
- `core_library` - Primary library to install (default: 'requests')
- `additional_packages` - Comma-separated list of extra packages
- `get_latest_stable_version` - Use stable versions only (default: True)

## Key Functions

### Installation Flow
- `_load_configuration()` - Reads config, constructs venv Python path
- `_start_library_installation()` - Creates worker thread, updates UI
- `LibraryInstallationWorker.run()` - Executes pip install with --report

### Pip Commands
```bash
# Version detection
{venv_python} -m pip index versions {library}

# Installation with report
{venv_python} -m pip install --report {logs_dir}/pip_install_report_{timestamp}.json {libraries...}

# Verification  
{venv_python} -m pip show {library}
```

### Report Parsing
- `_parse_install_report()` - Extracts index URL from JSON
- `_check_queues()` - Monitors worker progress/results
- `_verify_installation()` - Runs pip show, updates checklist

## Result Tuple
Worker returns: `(success: bool, message: str, report_path: str, stdout: str, stderr: str)`

## Running Tests
```bash
cd installer
python -m unittest install_gui.steps.test_libray_step -v
```

**Test Coverage:** 13 tests - pip report parsing, worker behavior, error handling