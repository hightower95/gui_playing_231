# Artifactory Configuration Step Documentation

## Overview

The Artifactory Configuration Step (`ArtifactorySetupStep`) handles the setup of private package repository access by configuring pip to use an Artifactory index-url. This step is positioned after folder selection and before virtual environment creation in the installation sequence.

## Architecture

### Class Hierarchy
```
BaseStep (abstract)
└── ArtifactorySetupStep
    ├── Uses pyirc_bootstrapper utilities
    └── Integrates with shared state system
```

### Key Dependencies
- **pyirc_bootstrapper**: Utilities for pip configuration management
- **tkinter**: Native UI components
- **webbrowser**: URL opening functionality
- **configparser**: Configuration file processing

## Step Flow

### 1. Initialization
```python
def __init__(self, installation_settings, shared_state):
    # Load URLs from configuration
    self.token_url = installation_settings.get('Step_Artifactory', 'token_url')
    self.guide_url = installation_settings.get('Step_Artifactory', 'guide_url')
    
    # Initialize state tracking
    self._is_configured = False
```

**Configuration Requirements:**
- `[Step_Artifactory]` section in `install_settings.ini`
- `token_url`: URL to Artifactory token generation page
- `guide_url`: URL to configuration guide/documentation

### 2. UI Creation Flow

#### 2.1 Existing Configuration Detection
```python
def _check_existing_configuration(self) -> bool:
    # Check simulation mode first
    if self._check_simulation_mode():
        return True
    
    # Check actual pip configuration
    if pip_exists_with_correct_sections():
        self._show_configured_state()
        return True
```

**Behavior:**
- **Simulation Mode**: Shows "✅ Artifactory (simulated)" if `simulate_artifactory_complete=true`
- **Existing Config**: Shows "✅ Artifactory already configured" if pip.ini exists with [global] section
- **No Config**: Proceeds to full UI creation

#### 2.2 Full UI Components

**Instruction Panel:**
```python
instruction_frame = ttk.Frame(frame)
howto_btn = ttk.Button("How To Configure", command=self._show_instructions)
artifactory_btn = ttk.Button("Open Artifactory", command=self._open_token_url)  
guide_btn = ttk.Button("Open Guide", command=self._open_guide_url)
```

**Configuration Input:**
```python
self.url_entry = tk.Text(height=4, width=80, wrap=tk.WORD)
# Multi-line text widget with placeholder support
```

**Status Indicators:**
```python
self.index_url_status = ttk.Label(text="⏸ Not configured")
self.token_status = ttk.Label(text="")
```

### 3. User Interaction Flow

#### 3.1 Help System
```python
def _show_instructions(self):
    """Display detailed configuration instructions in popup"""
    messagebox.showinfo("Artifactory Configuration Instructions", 
                       self.howto_instructions)
```

#### 3.2 URL Opening
```python
def _open_token_url(self):
    """Open Artifactory token generation page"""
    webbrowser.open(self.token_url)
    # Logs: "Artifactory step: Opening token URL: {url}"

def _open_guide_url(self):
    """Open configuration guide"""
    webbrowser.open(self.guide_url)
    # Logs: "Artifactory step: Opening guide URL: {url}"
```

#### 3.3 Real-time Validation
```python
def _validate_url_input(self, event=None):
    # Skip if placeholder showing
    if self.showing_placeholder:
        self._is_configured = False
        return
    
    # Get user input
    url = self.url_entry.get("1.0", tk.END).strip()
    
    # Validate using pyirc_bootstrapper
    is_valid, error_msg = is_valid_index_url_value(url)
    
    if is_valid:
        self._is_configured = True
        self.index_url_status.config(text="✅ Valid configuration")
    else:
        self._is_configured = False
        self.index_url_status.config(text=f"❌ {error_msg}")
```

## .pyirc File Integration

### Configuration File Location
```python
# From pyirc_bootstrapper.py
APP_DATA = os.getenv('APPDATA')  # e.g., C:\Users\username\AppData\Roaming
pip_config_dir = os.path.join(APP_DATA, 'pip')
pip_config_file = os.path.join(pip_config_dir, 'pip.ini')
```

### Validation Functions

#### 1. Configuration Validation
```python
def is_valid_index_url_value(test_value: str) -> Tuple[bool, str]:
    """Validates pip configuration format"""
    
    # Required format checks:
    # 1. Must start with "[global]"
    # 2. Must contain "index-url =" line
    # 3. Must point to "common-pypi/simple"
    
    if not test_value.startswith("[global]"):
        return False, "index-url must start with [global]"
    
    if not "index-url =" in test_value:
        return False, "index-url line missing"
    
    if not "common-pypi/simple" in test_value:
        return False, "index-url must point to common-pypi/simple"
    
    return True, ""
```

#### 2. Existing Configuration Detection
```python
def pip_exists_with_correct_sections() -> bool:
    """Check if pip config exists with required sections"""
    
    if not os.path.isfile(pip_config_file):
        return False
    
    config = configparser.ConfigParser()
    config.read(pip_config_file)
    
    return config.has_option("global", "index-url")
```

### Configuration Saving Process

#### Step-by-Step Save Operation
```python
def complete_step(self) -> bool:
    """Main save operation in complete_step method"""
    
    # 1. Get validated user input
    pyirc_entry_value = self.url_entry.get("1.0", tk.END).strip()
    is_valid, error_msg = is_valid_index_url_value(pyirc_entry_value)
    
    # 2. Load/create pip configuration
    config = get_pip_config(create_if_not_exists=True)
    temp_config = configparser.ConfigParser()
    temp_config.read_string(pyirc_entry_value)
    
    # 3. Handle existing configuration
    if config.has_option('global', 'index-url'):
        existing_url = config.get('global', 'index-url')
        logging.info(f"Overwriting existing index-url: {existing_url}")
        config.remove_option('global', 'index-url')
    
    # 4. Merge new configuration
    for section_name in temp_config.sections():
        if not config.has_section(section_name):
            config.add_section(section_name)
        
        for key, value in temp_config[section_name].items():
            config.set(section_name, key, value)
    
    # 5. Save to file
    if save_pip_config(config):
        self._is_configured = True
        self.update_shared_state("artifactory_configured", True)
        self.mark_completed()
        return True
```

#### Configuration File Management
```python
def get_pip_config(create_if_not_exists: bool = False) -> configparser.ConfigParser:
    """Load or create pip configuration"""
    
    # Ensure directory exists
    if create_if_not_exists and not os.path.isdir(pip_config_dir):
        os.makedirs(pip_config_dir, exist_ok=True)
    
    # Load existing or create new
    user_config = configparser.ConfigParser()
    if os.path.isfile(pip_config_file):
        user_config.read(pip_config_file)
    
    return user_config

def save_pip_config(config: configparser.ConfigParser) -> bool:
    """Save configuration to pip.ini"""
    
    os.makedirs(pip_config_dir, exist_ok=True)
    try:
        with open(pip_config_file, 'w') as f:
            config.write(f)
        return True
    except Exception as e:
        logging.error(f"Failed to save pip config: {e}")
        return False
```

## Function Reference

### Core Step Methods (Required by BaseStep)

#### get_title() -> str
Returns: `"Configure Artifactory"`

#### get_description() -> str
Returns: `"Set up access to your organization's private package repository"`

#### get_hint_text() -> str
Returns: `"Follow the instructions to get your Artifactory configuration"`

#### can_complete() -> bool
```python
def can_complete(self) -> bool:
    return self._is_configured or pip_exists_with_correct_sections()
```

#### complete_step() -> bool
Main orchestration method that:
1. Validates input
2. Processes configuration
3. Saves to .pyirc file
4. Updates shared state
5. Marks step completed

### UI Management Methods

#### create_widgets(parent_frame)
Creates complete UI including:
- Instruction panels with buttons
- Multi-line text input with placeholder
- Real-time validation status
- Tooltips for help buttons

#### _setup_placeholder()
Manages placeholder text in input field:
```python
self.placeholder_text = "[global]\nindex-url = https://token@example.com/artifactory/api/pypi/common-pypi/simple"
```

#### _validate_url_input(event=None)
Real-time validation triggered on:
- KeyRelease events
- Focus changes
- Manual calls

### Event Handlers

#### Focus Management
```python
def _on_entry_focus_in(self, event):
    """Remove placeholder on focus"""
    
def _on_entry_focus_out(self, event):
    """Restore placeholder if empty"""
    
def _on_entry_click(self, event):
    """Clear placeholder on click"""
```

#### URL Operations
```python
def _open_token_url(self):
    """Open Artifactory token page with logging"""
    
def _open_guide_url(self):
    """Open configuration guide with logging"""
    
def _show_instructions(self):
    """Display help popup"""
```

### Configuration Detection

#### _check_existing_configuration() -> bool
Orchestrates detection of existing configuration

#### _check_simulation_mode() -> bool
Checks `simulate_artifactory_complete` setting

#### _show_configured_state()
Displays simple "already configured" message

#### _show_simulated_state()
Displays "simulated" status for testing

### Utility Integration

#### Tooltip System
```python
def _create_tooltip(self, widget, text):
    """Creates hover tooltips with multi-line support"""
    # Handles mouse enter/leave events
    # Creates temporary popup windows
    # Supports formatted instruction text
```

## State Management

### Internal State Variables
```python
self._is_configured: bool           # Tracks if configuration is valid
self.showing_placeholder: bool      # UI placeholder state
self.token_url: str                # Artifactory token URL
self.guide_url: str                # Configuration guide URL
```

### Shared State Integration
```python
# Sets when configuration is saved successfully
self.update_shared_state("artifactory_configured", True)

# Used by subsequent steps to verify Artifactory setup
artifactory_ready = self.get_shared_state("artifactory_configured", False)
```

## Configuration Requirements

### install_settings.ini
```ini
[Step_Artifactory]
token_url = https://your-artifactory.com/get-token
guide_url = https://your-wiki.com/artifactory-setup

[DEV]
# Testing/simulation
simulate_artifactory_complete = false
```

### Expected User Input Format
```ini
[global]
index-url = https://username:token@your-artifactory.com/artifactory/api/pypi/common-pypi/simple
```

## Error Handling

### Validation Errors
- Empty input: "index-url must not be empty"
- Wrong format: "index-url must start with [global]"
- Missing line: "index-url line missing"
- Wrong URL: "index-url must point to common-pypi/simple"

### File System Errors
- Directory creation failures
- Permission issues
- Configuration file write errors

### Recovery Mechanisms
- Graceful fallbacks for URL opening failures
- Clear error messages for user guidance
- Logging for debugging support

## Integration Points

### Pre-requisites
- Folder selection step must be completed
- Installation path must be available in shared state

### Subsequent Steps
- Virtual environment creation uses artifactory configuration
- Library installation leverages private repository access

### Logging Integration
- All user actions logged with INFO level
- Configuration operations logged with DEBUG level
- Errors logged with ERROR level
- URLs and sensitive data logged safely (truncated)

## Testing Support

### Simulation Mode
Enable via `simulate_artifactory_complete=true` in configuration

### Manual Testing
1. Configure test URLs in install_settings.ini
2. Use placeholder text for format validation
3. Test with various invalid inputs
4. Verify .pyirc file creation and content

### Automated Testing
- Mock pyirc_bootstrapper functions
- Test validation logic with known inputs
- Verify state management and callbacks
- Test UI component creation and behavior