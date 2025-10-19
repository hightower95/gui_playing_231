# Component Library - Quick Reference Guide

**Phase 1 & 2 Components**

This is a quick-reference guide for developers. Copy-paste these examples to get started quickly.

---

## 🚀 Import Statement

```python
from app.ui.components import (
    # Interactive Components
    StandardCheckBox,
    StandardProgressBar,
    StandardRadioButton, create_radio_group,
    StandardTextArea,
    StandardSpinBox,
    StandardGroupBox,
    # Layout Components
    StandardFormLayout,
    StandardWarningDialog, DialogResult,
    # Also available
    StandardButton, ButtonRole, ButtonSize,
    StandardLabel, TextStyle,
    StandardComboBox, ComboSize,
    StandardInput,
)
```

---

## 📋 Common Patterns

### 1. Create a Simple Form

```python
def create_settings_form(self):
    """Create a settings form with sections"""
    form = StandardFormLayout(label_width=120)
    
    # Basic section
    form.add_section("Connection Settings")
    form.add_row("Host:", StandardInput(placeholder="localhost"))
    form.add_row("Port:", StandardSpinBox(min_value=1, max_value=65535, default_value=8080))
    
    # Options section
    form.add_section("Options")
    form.add_widget(StandardCheckBox("Enable auto-connect", checked=True))
    form.add_widget(StandardCheckBox("Use SSL"))
    form.add_spacing(10)
    form.add_row("Timeout:", StandardSpinBox(min_value=1, max_value=300, suffix=" sec"))
    
    return form
```

### 2. Show Confirmation Dialog

```python
def delete_item_with_confirmation(self):
    """Delete item after user confirms"""
    result = StandardWarningDialog.show_yes_no(
        self,
        "Confirm Delete",
        "Are you sure you want to delete this item? This cannot be undone."
    )
    
    if result == DialogResult.YES:
        self.perform_delete()
        StandardWarningDialog.show_info(self, "Success", "Item deleted successfully!")
```

### 3. Save Changes Dialog

```python
def close_with_save_prompt(self):
    """Prompt user to save changes before closing"""
    if self.has_unsaved_changes():
        result = StandardWarningDialog.show_yes_no_cancel(
            self,
            "Save Changes",
            "Do you want to save your changes before closing?"
        )
        
        if result == DialogResult.YES:
            self.save_changes()
            self.close()
        elif result == DialogResult.NO:
            self.close()
        # else CANCEL - do nothing, stay on page
    else:
        self.close()
```

### 4. Progress Indicator for Long Operation

```python
def process_large_file(self, file_path: str):
    """Process file with progress indicator"""
    # Setup progress bar
    progress = StandardProgressBar(show_percentage=True)
    self.layout.addWidget(progress)
    
    # Get total rows
    total_rows = self.count_rows(file_path)
    progress.set_range(0, total_rows)
    
    # Process rows
    for i, row in enumerate(self.read_file(file_path)):
        self.process_row(row)
        progress.set_value(i + 1)
        QApplication.processEvents()  # Keep UI responsive
    
    # Done
    progress.set_value(total_rows)
    StandardWarningDialog.show_info(self, "Complete", f"Processed {total_rows} rows!")
```

### 5. Radio Button Group for Mode Selection

```python
def create_mode_selector(self):
    """Create radio button group for mode selection"""
    # Create radio buttons
    self.radio_connect = StandardRadioButton("Use E3 Connect", checked=True)
    self.radio_cache = StandardRadioButton("Use E3 Cache")
    self.radio_manual = StandardRadioButton("Manual Mode")
    
    # Group them (ensures mutual exclusion)
    self.mode_group = create_radio_group(
        self.radio_connect,
        self.radio_cache,
        self.radio_manual,
        default_index=0
    )
    
    # Connect signals
    self.radio_connect.toggled.connect(lambda checked: self.on_mode_changed("connect") if checked else None)
    self.radio_cache.toggled.connect(lambda checked: self.on_mode_changed("cache") if checked else None)
    self.radio_manual.toggled.connect(lambda checked: self.on_mode_changed("manual") if checked else None)
    
    # Add to layout
    layout = QVBoxLayout()
    layout.addWidget(self.radio_connect)
    layout.addWidget(self.radio_cache)
    layout.addWidget(self.radio_manual)
    return layout
```

### 6. Group Box with Related Options

```python
def create_export_options(self):
    """Create group box with export options"""
    group = StandardGroupBox("Export Options")
    layout = QVBoxLayout()
    
    # Add checkboxes
    self.export_headers = StandardCheckBox("Include headers", checked=True)
    self.export_index = StandardCheckBox("Include index column")
    self.export_timestamp = StandardCheckBox("Add timestamp")
    
    layout.addWidget(self.export_headers)
    layout.addWidget(self.export_index)
    layout.addWidget(self.export_timestamp)
    
    # Add format selector
    layout.addWidget(StandardLabel("Format:", style=TextStyle.LABEL))
    self.format_combo = StandardComboBox(size=ComboSize.SINGLE, items=["CSV", "Excel", "JSON"])
    layout.addWidget(self.format_combo)
    
    group.setLayout(layout)
    return group
```

### 7. Text Area for Logs/Results

```python
def setup_log_area(self):
    """Setup read-only text area for logs"""
    self.log_area = StandardTextArea(
        read_only=True,
        height=200
    )
    
    # Connect to logging
    self.log_signal.connect(self.append_log)
    
    return self.log_area

def append_log(self, message: str):
    """Append message to log area"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    self.log_area.append_text(f"[{timestamp}] {message}\n")
```

### 8. Complete Configuration Dialog

```python
class ConfigurationDialog(QDialog):
    """Complete configuration dialog example"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setMinimumWidth(500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Form
        form = StandardFormLayout(label_width=140)
        
        # Basic settings
        form.add_section("Basic Settings")
        self.name_input = StandardInput(placeholder="Enter name...")
        form.add_row("Project Name:", self.name_input)
        
        self.version_combo = StandardComboBox(size=ComboSize.SINGLE, items=["v1.0", "v2.0", "v3.0"])
        form.add_row("Version:", self.version_combo)
        
        # Advanced settings
        form.add_section("Advanced Settings")
        
        self.timeout_spin = StandardSpinBox(min_value=1, max_value=300, default_value=30, suffix=" sec")
        form.add_row("Timeout:", self.timeout_spin)
        
        self.retry_spin = StandardSpinBox(min_value=0, max_value=10, default_value=3)
        form.add_row("Retry Attempts:", self.retry_spin)
        
        # Options
        form.add_section("Options")
        self.auto_save = StandardCheckBox("Auto-save enabled", checked=True)
        form.add_widget(self.auto_save)
        
        self.debug_mode = StandardCheckBox("Debug mode")
        form.add_widget(self.debug_mode)
        
        # Add form to main layout
        main_layout.addLayout(form)
        main_layout.addStretch()
        
        # Buttons
        button_row = self._create_buttons()
        main_layout.addWidget(button_row)
    
    def _create_buttons(self):
        """Create button row"""
        from app.ui.components import create_button_row
        
        save_btn = StandardButton("Save", role=ButtonRole.PRIMARY, size=ButtonSize.COMPACT)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = StandardButton("Cancel", role=ButtonRole.SECONDARY, size=ButtonSize.COMPACT)
        cancel_btn.clicked.connect(self.reject)
        
        return create_button_row(save_btn, cancel_btn)
    
    def get_config(self):
        """Get configuration values"""
        return {
            "name": self.name_input.get_text(),
            "version": self.version_combo.get_selected_text(),
            "timeout": self.timeout_spin.get_value(),
            "retry_attempts": self.retry_spin.get_value(),
            "auto_save": self.auto_save.is_checked(),
            "debug_mode": self.debug_mode.is_checked()
        }
```

---

## 🎯 Anti-Patterns (Don't Do This!)

### ❌ Don't manually style components

```python
# WRONG
checkbox = StandardCheckBox("Enable feature")
checkbox.setStyleSheet("color: red; background: blue;")  # Breaks consistency!

# RIGHT
checkbox = StandardCheckBox("Enable feature")
# Use component as-is, or create a new variant if needed
```

### ❌ Don't create manual form layouts

```python
# WRONG - Manual form creation (verbose, inconsistent)
layout = QVBoxLayout()
row1 = QHBoxLayout()
label1 = QLabel("Name:")
label1.setFixedWidth(120)
input1 = QLineEdit()
row1.addWidget(label1)
row1.addWidget(input1)
layout.addLayout(row1)
# ... repeat for each row

# RIGHT - Use StandardFormLayout
form = StandardFormLayout()
form.add_row("Name:", StandardInput())
```

### ❌ Don't use QMessageBox directly

```python
# WRONG - Verbose QMessageBox setup
msg_box = QMessageBox(self)
msg_box.setWindowTitle("Confirm")
msg_box.setText("Are you sure?")
msg_box.setIcon(QMessageBox.Icon.Question)
msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
result = msg_box.exec()

# RIGHT - Use StandardWarningDialog
result = StandardWarningDialog.show_yes_no(self, "Confirm", "Are you sure?")
```

### ❌ Don't manually create progress bars

```python
# WRONG - Manual setup
progress = QProgressBar()
progress.setMinimum(0)
progress.setMaximum(100)
progress.setValue(0)
progress.setTextVisible(True)
progress.setStyleSheet("... lots of CSS ...")

# RIGHT - Use StandardProgressBar
progress = StandardProgressBar(show_percentage=True)
```

---

## 💡 Tips & Tricks

### Tip 1: Use DialogResult enum for type safety
```python
result = StandardWarningDialog.show_yes_no(self, "Title", "Message")

# Type-safe comparison
if result == DialogResult.YES:  # ✅ IDE autocomplete
    proceed()

# Don't use magic numbers
if result == 1:  # ❌ What does 1 mean?
    proceed()
```

### Tip 2: Form sections for organization
```python
form = StandardFormLayout()

form.add_section("User Information")  # Creates visual section header
form.add_row("Name:", StandardInput())
form.add_row("Email:", StandardInput())

form.add_section("Preferences")  # Another section
form.add_widget(StandardCheckBox("Enable notifications"))
```

### Tip 3: Connect progress to value_changed signal
```python
progress = StandardProgressBar()
progress.value_changed.connect(lambda v: print(f"Progress: {v}%"))

# Now every update is logged
for i in range(101):
    progress.set_value(i)  # Triggers signal
```

### Tip 4: Use tristate checkboxes for "Select All"
```python
select_all = StandardCheckBox("Select All", tristate=True)
select_all.state_changed.connect(self.handle_select_all)

def handle_select_all(self, state):
    if state == Qt.Checked:
        self.select_all_items()
    elif state == Qt.Unchecked:
        self.deselect_all_items()
    # Qt.PartiallyChecked - some selected
```

### Tip 5: SpinBox suffix for units
```python
# Clear unit indication
timeout = StandardSpinBox(min_value=1, max_value=300, suffix=" sec")
width = StandardSpinBox(min_value=100, max_value=1000, suffix=" px")
percentage = StandardSpinBox(min_value=0, max_value=100, suffix=" %")

# User sees "30 sec", "500 px", "75 %" in the UI
```

---

## 📚 See Also

- **Full Documentation:** `app/ui/components/README.md`
- **Demo Application:** `swiss_army_tool/demo_components_phase1_2.py`
- **Implementation Summary:** `app/ui/components/PHASE_1_2_SUMMARY.md`
- **Future Roadmap:** `app/ui/components/ADDITIONAL_COMPONENTS_ANALYSIS.md`

---

**Questions?** Check the README or run the demo!
