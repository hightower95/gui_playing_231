# VenvStep Architecture

## Purpose
The CreateVenvStep is responsible for checking for and creating a Python virtual environment. It returns only the **venv_path** (absolute path) to the conductor.

## Core Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CreateVenvStep                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Step Initialization                         │
│  • Read config: venv_name from [Paths].default_venv            │
│  • Check simulation mode: [DEV].simulate_venv_complete         │
│  • Get installation_path from shared_state                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UI Creation                               │
│  • Status label (Ready/Creating/Success/Error)                 │
│  • Create Environment button                                   │
│  • Progress bar (hidden initially)                             │
│  • Output text area (hidden initially)                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │ User clicks   │ ─── Simulation? ────┐
                        │ "Create Env"  │                     │
                        └───────────────┘                     │
                                │                             │
                                ▼                             ▼
                    ┌─────────────────────┐         ┌─────────────────┐
                    │   Validate Setup    │         │  Skip Creation  │
                    │  • Check install    │         │  Return fake    │
                    │    path exists      │         │  venv_path      │
                    │  • Find Python exe  │         │                 │
                    │  • Calculate venv   │         │                 │
                    │    full path        │         │                 │
                    └─────────────────────┘         └─────────────────┘
                                │                             │
                                ▼                             │
                    ┌─────────────────────┐                   │
                    │  Background Thread  │                   │
                    │  VenvCreationWorker │                   │
                    │                     │                   │
                    │  1. Remove old venv │                   │
                    │  2. Run python -m   │                   │
                    │     venv <path>     │                   │
                    │  3. Verify creation │                   │
                    └─────────────────────┘                   │
                                │                             │
                                ▼                             │
                        ┌───────────────┐                     │
                        │   Success?    │                     │
                        └───────────────┘                     │
                              │   │                           │
                         Yes  │   │ No                        │
                              ▼   ▼                           │
                    ┌─────────────────────┐                   │
                    │   Update UI State   │                   │
                    │  • Show result      │                   │
                    │  • Enable/disable   │                   │
                    │    button           │                   │
                    └─────────────────────┘                   │
                                │                             │
                                ▼                             │
                        ┌───────────────┐                     │
                        │ can_complete? │ ◄───────────────────┘
                        └───────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │complete_step()│
                        │               │
                        │ ONLY updates  │
                        │ shared_state: │
                        │ venv_path =   │
                        │ /abs/path/to  │
                        │ /.test_venv   │
                        └───────────────┘
```

## Key Components

### 1. Configuration Reader
- **Purpose**: Read venv settings from install_settings.ini
- **Key Settings**:
  - `[Paths].default_venv` → venv directory name (e.g., ".test_venv")
  - `[DEV].simulate_venv_complete` → skip actual creation for testing

### 2. State Manager  
- **Input**: `shared_state['valid_installation_path']` from previous step
- **Output**: `shared_state['venv_path']` = absolute path to venv
- **Derivable elsewhere**:
  - venv_python_path = venv_path + "/Scripts/python.exe" (Windows)
  - venv_name = Path(venv_path).name
  - installation_directory = Path(venv_path).parent

### 3. Environment Validator
- **Find Python**: sys.executable → python → python3 → py
- **Test Python**: Check `python --version` and `python -m venv --help`
- **Path Validation**: Ensure installation path exists and is writable

### 4. VenvCreationWorker (QThread)
- **Prevents UI blocking** during potentially slow venv creation
- **Progress updates** via Qt signals
- **Commands executed**:
  ```bash
  python -m venv /absolute/path/to/installation/.test_venv
  ```

### 5. UI State Machine
```
Ready → Creating → Success/Error → Ready (for recreation)
  ↓       ↓           ↓
Button  Progress    Result
Enabled   Bar      Message
```

## Simplified Responsibilities

| Component | Responsibility | Output |
|-----------|----------------|---------|
| **Config Reader** | Read venv_name, simulation mode | String values |
| **Path Calculator** | installation_path + venv_name | Absolute venv_path |
| **Python Finder** | Locate suitable Python executable | Python command |
| **Worker Thread** | Execute `python -m venv` safely | Success/failure |
| **State Updater** | Store result in shared_state | `venv_path` only |

## Method Organization (Current vs Desired)

### Current: 30+ methods in one file 😰
- Configuration methods (5)
- UI creation methods (8) 
- Validation methods (4)
- Threading methods (6)
- State management (7)

### Desired: Split into focused modules 😊

```
venv_step.py (main class - 10 methods)
├── venv_config.py (configuration reading)
├── venv_validator.py (Python detection, path validation)
├── venv_worker.py (background creation thread)
└── venv_ui.py (UI state management)
```

## Essential Public Interface

```python
class CreateVenvStep(BaseStep):
    def get_title() -> str
    def get_description() -> str  
    def get_hint_text() -> str
    def can_complete() -> bool
    def create_widgets(parent, layout)
    def complete_step() -> bool  # Only sets venv_path in shared_state
```

## Data Flow Summary

```
Config File → venv_name (.test_venv)
Shared State → installation_path (/path/to/install)
User Action → Create Environment button
Background → python -m venv /path/to/install/.test_venv  
Result → shared_state['venv_path'] = '/path/to/install/.test_venv'
```

## ✅ IMPLEMENTATION RESULTS

### Shared State Minimalism Achieved

**Before: 6 keys stored** ❌
```python
shared_state = {
    'valid_installation_path': '...',
    'venv_created': True,
    'venv_path': '...',
    'venv_name': '.test_venv', 
    'venv_python_path': '...',
    'installation_directory': '...'
}
```

**After: 2 keys stored** ✅
```python
shared_state = {
    'valid_installation_path': '...',
    'venv_path': '/absolute/path/to/.test_venv'
}
```

### Dynamic Derivation Works
```python
from venv_utils import VenvPathUtils

# All information derived from venv_path
venv_info = VenvPathUtils.enrich_shared_state(shared_state)
# Returns: venv_python_path, venv_pip_path, venv_name, etc.

# Or use convenience functions
python_exe = get_python_executable_from_shared_state(shared_state)
```

### File Organization Improved
- **venv_step.py**: Core step logic (simplified)
- **venv_utils.py**: Path derivation utilities 
- **venv_step.md**: Architecture documentation

**Everything else can be derived from venv_path when needed!**