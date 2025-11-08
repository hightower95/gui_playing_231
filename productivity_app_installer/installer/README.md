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

## Testing Upgrade Logic

When modifying `run_app.pyw` or its template:
```bash
python test_upgrade_logic.py --demo    # Test all upgrade scenarios
python test_upgrade_logic.py --verbose # Run full test suite
```

## Launch Configuration (launch_config.ini)

App Versions should be assumed so:
- Odd minor versions (x.1.x, x.3.x) should be assumed unstable
- Even minor versions (x.2.x, x.6.x) are available for general release

Generated app uses granular upgrade controls:

```ini
# Automatic upgrade permissions
auto_upgrade_major_version = false     # Workflow changes (breaking)
auto_upgrade_minor_version = true      # Feature updates (safe)  
auto_upgrade_patches = true            # Bug fixes (always safe)

# Test release handling
allow_upgrade_to_test_releases = false # Odd minor versions (1.1.x, 1.3.x)
```

**Upgrade Behavior:**
- **Major** (2.0.0): Workflow changes, usually manual
- **Minor** (1.2.0): New features, often auto-enabled
- **Patch** (1.2.1): Bug fixes, typically auto-enabled
- **Test** (1.1.x): Unstable releases, manual opt-in

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