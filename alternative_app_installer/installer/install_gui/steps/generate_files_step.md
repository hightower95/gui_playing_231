# Generate Files Step Documentation

## Process Flow

```
┌─────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐
│     create_widgets()    │───▶│    Target Folder UI      │───▶│    _create_checklist()   │
└─────────────────────────┘    └──────────────────────────┘    └──────────────────────────┘
                                           │                                    │
                                           ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              [Generate Files] Button                                    │
└─────────────────────────┬───────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────────────────────┐
│                    _start_file_generation()                                             │
└─────────────────────────┬───────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│ _generate_run_  │ │_generate_update_│ │_generate_launch_│ │  _clone_utils_      │
│   app()         │ │   app()         │ │   config()      │ │    directory()      │
│                 │ │                 │ │                 │ │                     │
│ Template →      │ │ Template →      │ │ Template +      │ │ Source → Target     │
│ run_app.pyw     │ │ update_app.pyw  │ │ Shared State → │ │ /utils → /utils     │
│                 │ │                 │ │ launch_config.  │ │                     │
│                 │ │                 │ │ ini             │ │                     │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────────┘
```

## Templates and Substitutions

### Template Files
- `run_app.pyw.template` - Main application launcher
- `update_app.pyw.template` - Update manager GUI
- `launch_config.ini.template` - Configuration with placeholders

### Launch Config Substitutions
```ini
{{VENV_PYTHON_PATH}} - Absolute path to venv Python executable
{{VENV_DIR_PATH}} - Absolute path to venv directory  
{{VENV_DIR_NAME}} - Name of venv directory
{{LIBRARY_NAME}} - Core library name from shared state
{{ALWAYS_UPGRADE}} - Auto-upgrade setting (true/false)
{{ALLOW_UPGRADE_TO_TEST_RELEASES}} - Test release upgrades (true/false)
{{ENABLE_LOG}} - Logging enabled (true/false)
{{LOG_LEVEL}} - Log level (INFO, DEBUG, etc.)
{{INSTALLED_FOLDER}} - Installation folder path
{{INSTALLER_VERSION}} - Version of installer used
{{INSTALLATION_DATE}} - Date/time of installation
```

## Shared State Dependencies

**Required from previous steps:**
- `venv_path` - Virtual environment directory path
- `installation_folder` - Target installation folder
- `core_library` - Primary library name

**Configuration Sources:**
- `[Step_Install_Libraries]` section: `always_upgrade`, `allow_upgrade_to_test_releases`
- `[DEFAULT]` section: `enable_log`, `log_level`

## Generated Files

1. **run_app.pyw** - Main launcher with:
   - Virtual environment discovery
   - Intelligent version management
   - Library execution with launch config

2. **update_app.pyw** - Update manager with:
   - Version listing GUI
   - Manual upgrade capability
   - Current version display

3. **launch_config.ini** - Runtime configuration from installer state

4. **utils/** - Runtime utility modules:
   - `simple_venv_discovery.py` - VEnv path resolution
   - `__init__.py` - Version management and logging utilities

## UI Flow
1. User selects target folder via Browse button
2. Generate Files button becomes enabled
3. Checklist shows progress of each generation step
4. Success dialog shows completion

## Running Tests
```bash
cd installer
python -c "from install_gui.steps import GenerateFilesStep; print('Import OK')"
```