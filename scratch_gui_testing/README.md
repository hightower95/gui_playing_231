# Live Ping Monitor GUI

A simple Windows GUI application for monitoring continuous ping operations with live output.

## Files

- **`ui.py`** - Main GUI application with start button and read-only text area
- **`ping.py`** - Ping controller module with `start_pinging(ip: str)` method
- **`run.py`** - Quick launcher script

## Features

- 🚀 **Start/Stop Controls** - Easy ping management
- 📊 **Live Output** - Real-time ping results with timestamps
- 🎯 **Target Input** - Enter any IP address or hostname
- 🧹 **Clear Output** - Clean the display when needed
- ⏱️ **Timestamped Results** - Each ping shows the time it occurred
- 🛑 **Graceful Shutdown** - Properly stops ping when closing

## Usage

### Running the Application

```bash
# Using the Python virtual environment
C:/Users/peter/OneDrive/Documents/Coding/gui/.venv/Scripts/python.exe ui.py

# Or use the quick runner
C:/Users/peter/OneDrive/Documents/Coding/gui/.venv/Scripts/python.exe run.py
```

### Using the GUI

1. **Enter Target**: Type an IP address or hostname (default: 8.8.8.8)
2. **Start Ping**: Click "🚀 Start Ping" or press Enter
3. **Monitor Output**: Watch live ping results in the text area
4. **Stop Ping**: Click "🛑 Stop Ping" when done
5. **Clear Output**: Click "🗑️ Clear Output" to clean the display

### Example Targets

- `8.8.8.8` - Google DNS (default)
- `1.1.1.1` - Cloudflare DNS
- `google.com` - Google website
- `github.com` - GitHub website
- `192.168.1.1` - Typical router IP

## Technical Details

### ping.py Module

```python
from ping import PingController

# Create controller with output callback
controller = PingController(output_callback_function)

# Start continuous ping (-t parameter)
controller.start_pinging("8.8.8.8")

# Stop ping
controller.stop_pinging()
```

### ui.py Features

- **PySide6 GUI** - Modern Qt-based interface
- **Thread-safe Output** - Qt signals for cross-thread communication
- **Auto-scroll** - Always shows latest ping results
- **Memory Management** - Limits output length to prevent memory issues
- **Error Handling** - Graceful handling of network and input errors

### Live Updates Implementation

The application uses:
1. **Threading** - Ping runs in separate thread to avoid UI blocking
2. **Qt Signals** - Thread-safe communication between ping thread and GUI
3. **Real-time Display** - Output appears immediately as ping results arrive
4. **Continuous Mode** - Uses Windows `ping -t` for continuous pinging

## Styling

The GUI includes:
- Clean, modern appearance
- Green color scheme for network theme
- Monospace font for ping output
- Responsive button states
- Professional grouping and spacing

## Error Handling

- Invalid IP/hostname input validation
- Network connectivity error messages
- Graceful ping process termination
- UI state management during errors