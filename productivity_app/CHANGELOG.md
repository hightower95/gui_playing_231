# Changelog

All notable changes to Productivity App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Renamed project from "Swiss Army Tool" to "Productivity App"
- Updated all branding and package names to "productivity-app"

## [0.1.0] - 2025-10-31

### Added

#### Core Infrastructure
- Modern Python packaging with PEP 621 compliant `pyproject.toml`
- Development environment setup with comprehensive `requirements-dev.txt`
- Build and distribution documentation (`BUILD.md`)
- Contributing guidelines (`CONTRIBUTING.md`)
- Generic `BackgroundWorker` and `ProgressiveBackgroundWorker` classes for threading
- Enhanced `AppContext` as full dependency injection container
- Improved base classes (`BasePresenter`, `BaseModel`) with practical helpers

#### Document Scanner
- Excel sheet selection feature for .xlsx files
- Ability to add same file multiple times with different sheets
- Document source type classification (local vs cached)
- Cached document metadata fields (version, timestamp, file_id, schema_version)
- Configuration export to JSON functionality
- Automatic sheet detection and dropdown selection

#### Code Quality
- Black code formatter configuration (line length: 100)
- isort import sorting with black-compatible profile
- mypy type checking configuration
- pytest configuration with coverage reporting
- flake8 linting setup
- Pre-commit hooks support

#### User Interface
- Declarative tab configuration system (`TAB_CONFIG`)
- Dynamic settings tab checkbox generation
- Simplified tab management in main window
- Improved tab visibility controls

### Changed

#### Refactoring
- Removed threading from configuration management (~250 lines eliminated)
- Simplified main window tab system (~200 lines reduction, 67% smaller)
- Refactored settings tab checkbox management (~150 lines eliminated)
- Enhanced base classes with working signals and practical methods
- Removed forced abstractions and broken design patterns

#### Architecture
- Migrated to MVP (Model-View-Presenter) pattern consistently
- Centralized dependency injection through `AppContext`
- Declarative configuration approach across modules
- Type hints added throughout codebase

### Fixed
- `AttributeError` in EPD model after BaseModel refactor
- BasePresenter signals now work correctly (inherits QObject)
- Excel file loading with openpyxl integration
- Configuration state management threading issues

### Removed
- Legacy `set_data()` method and `_data` dictionary from `BaseModel`
- Forced `_initialize_data()` abstract method from base classes
- Repetitive code in tab initialization
- Duplicate checkbox management code in settings
- Custom threading implementations (replaced with generic workers)

## [0.0.1] - 2024-10-16

### Added
- Initial release with core functionality
- Connector search and management
- EPD (Engineering Product Data) viewer
- Document Scanner with caching
- Azure DevOps integration
- Remote documentation viewer
- Basic settings management

---

## Version History Summary

- **0.1.0** - Major refactoring release with improved architecture and distribution setup
- **0.0.1** - Initial prototype release

[Unreleased]: https://github.com/yourusername/productivity-app/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/productivity-app/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/yourusername/productivity-app/releases/tag/v0.0.1
