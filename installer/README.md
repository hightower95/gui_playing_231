# Installer Update Guide

To clone this installer

## Quick Update Steps

1. **Configure Settings** - Check `installation_settings.ini`:
   - Set all DEV flags to `false` (simulate_*_complete, skip_local_index, auto_generate_files)
   - Update `app_name`, `version`, and `core_libraries` as needed
   - Verify `token_url` and `help_page` URLs are correct

2. **Package for Distribution**:
   - Zip the entire `installer/` directory
   - Name it descriptively (e.g., `MyApp_Installer_v1.0.0.zip`)

3. **Test Before Release**:
   - Extract zip to clean location
   - Run `python bootstrap.py` to verify installer works
   - Test all installation steps complete successfully

## Key Files
- `installation_settings.ini` - Main configuration
- `bootstrap.py` - Entry point for installation wizard
- `scripts/` - Core installer logic
- `templates/` - Generated application file templates

## Development Mode
Set DEV flags in `installation_settings.ini` to `true` for testing:
- `simulate_*_complete = true` - Skip actual installation steps
- `auto_generate_files = true` - Auto-generate files when prerequisites met
- `debug = true` - Show console output during operations