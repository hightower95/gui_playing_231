# GitHub Copilot Instructions

## Project Overview

This is a **multi-layered engineering productivity suite** comprising:
1. **Bootstrap Installer System** (`installer/`) - Tkinter-based setup wizard for deployment
2. **Main Productivity App** (`productivity_app/`) - PySide6 desktop application with modular architecture  
3. **Standalone GUI Components** (`main.py`, `bw_gui.py`) - Research/prototype PySide6 applications

The main architecture follows **MVP (Model-View-Presenter) pattern** with dependency injection via `AppContext`.

## Key Architecture Patterns

### 1. App Context & Dependency Injection
```python
# Central service registry pattern used throughout
context = AppContext()
context.register('config', ConfigManager())
epd_model = context.get('epd_model', EpdModel)  # Type-safe access
```

### 2. MVP with Signal-Based Communication
```python
# Control layers emit Qt signals for UI updates
class ControlLayer(QObject):
    update_left_panel = Signal(str, str, str)  # Signals, not direct UI manipulation
    
# UI components connect to these signals
self.control_layer.update_left_panel.connect(self.update_left_panel)
```

### 3. Modular Tab System
- Tabs auto-register via `TAB_CONFIG` in `main_window.py`
- Each module has separate `presenter`, `model`, `view` structure
- Lazy loading with configurable delays for performance

## Critical Development Workflows

### Building & Distribution
```bash
# Use the smart build script (auto-detects changes, manages versions)
python package_builder.py                    # Auto-increment patch
python package_builder.py --minor           # Increment minor version
python package_builder.py --no-increment    # Build without version change
```

### Installation System Debugging
The installer uses **simulation modes** for testing:
```ini
# installation_settings.ini
[DEV]
simulate_venv_complete = true     # Skip actual venv creation
simulate_library_complete = true # Skip library installation  
debug = true                      # Show console output
```

### Running the App
```bash
# Development mode
python -m productivity_app.main

# Deployed mode (after installer)
python run_app.pyw  # Uses virtual environment automation
```

## Project-Specific Conventions

### 1. File Naming & Structure
- **`.pyw` files**: Windows GUI executables (no console)
- **MVP organization**: `app/{module}/{model,view,presenter}.py`
- **Config files**: JSON in `.tool_config/` directory (auto-created)
- **Cache patterns**: `{module}_cache/` directories for persistent data

### 2. Configuration Management
```python
# Centralized config in ConfigManager
ConfigManager.initialize()  # Must call on startup
config_path = ConfigManager.get_config_path('document_scanner.json')
```

### 3. Qt Best Practices in this Codebase
- **Signal connections over direct calls**: Maintains loose coupling
- **Custom control layers**: Business logic separate from Qt widgets
- **Programmatic simulation**: `simulate_breakout_wire_click()` methods for testing

## Integration Points

### 1. Document Scanner Module
- Uses JSON config files for document registration
- Supports CSV, Excel, TXT with configurable columns
- Cache files in `document_scanner_cache/` with timestamps

### 2. Bootstrap Installer 
- **5-step wizard**: Folder → VEnv → PyIRC → Library → Files
- **Template engine**: Generates `run_app.pyw` from `templates/`
- **Thread-safe execution**: All operations use `@run_async()` decorator
- **Intelligent upgrades**: Smart version management with stable/test release handling
- **Upgrade logging**: Detailed `upgrade_history.log` tracking version changes

### 3. Component Communication
```python
# Cross-module communication via context
context.set_state('current_connector', connector_data)
other_module = context.get('connector_provider')
```

### 4. Intelligent Upgrade System
- **Version classification**: Even minors = stable (1.0.x, 1.2.x), Odd minors = test (1.1.x, 1.3.x)
- **Safe defaults**: Config parsing fails gracefully to `false` (no auto-upgrade)
- **Major version protection**: Never auto-upgrade across major versions
- **Upgrade history**: All version changes logged to `upgrade_history.log`
- **Configuration**: `always_upgrade=true` (default), `allow_upgrade_to_test_releases=false`

## Build System Details

### Package Structure
- **Main package**: `productivity_app/` (installable via pip)
- **Script entry point**: `app.main:main` in `pyproject.toml`
- **Development dependencies**: Full test/lint/format suite in `[dev]` extras

### Version Management
- **Automated**: `package_builder.py` detects code changes and increments appropriately
- **Git integration**: Refuses to build with uncommitted changes
- **Smart detection**: Monitors source files and configs for changes

## Common Debugging Patterns

### 1. Virtual Environment Issues
```bash
# Check venv status in installer
# Look for: "Venv Python path verified" in logs
# Location: installer/logs/setup_wizard.log
```

### 2. Module Loading Problems  
```python
# Tab loading controlled by TAB_CONFIG delays
# Check AppContext service registration
# Verify presenter classes are properly imported
```

### 3. Configuration Persistence
```python
# All configs in .tool_config/ directory
# Document scanner: document_scanner.json
# App settings: app_settings.json
```

## Windows-Specific Considerations

- **PowerShell commands**: Use `;` for command chaining
- **Path handling**: All paths use `pathlib.Path` for cross-platform compatibility
- **Console management**: `.pyw` files prevent console windows in deployment
- **Virtual environment**: Located in `.test_venv/Scripts/` structure

When modifying this codebase, always consider the multi-layer architecture and maintain the separation between installer, main app, and prototype components.

## Guidance:
- Do not create documentation files unless explicitly asked.
- It is ok to suggest creating documentation if it helps to clarify complex parts of the codebase.
- When renaming variables it is necessary to update all references to those variables throughout the codebase to maintain consistency and avoid errors.
- Consider python modules will be installed via pip and ensure import statements reflect this structure.
- Reuse existing functions and classes wherever possible to maintain consistency and reduce redundancy in the codebase.
- When editing *.template files do not use f-strings. The template engine is not compatible with them.
- Do not use the token '&&' when generating shell commands.
- Avoid using emojis within python scripts.