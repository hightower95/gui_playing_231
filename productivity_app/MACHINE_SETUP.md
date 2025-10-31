# Machine Setup Guide

## Setting Up on a New Machine

### 1. Clone/Pull the Repository

```bash
git clone <repository-url>
cd productivity_app
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -e .[dev]
```

### 3. Configure Machine-Specific Settings (Optional)

If you need different AppData folders on this machine:

```bash
# Copy the example config
copy productivity_app\app\core\local_config.example.py productivity_app\app\core\local_config.py
```

Edit `local_config.py`:
```python
# Customize for this machine
APPDATA_ROOT_FOLDER = "MyToolsOnThisMachine"
```

This file is in `.gitignore` and won't be committed.

### 4. Run the Application

```bash
python run.py
```

## Git Workflow for Multiple Machines

### On Development Machine (Machine A)

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main
```

### On Other Machine (Machine B)

```bash
# Pull latest changes
git pull origin main

# Your local_config.py is preserved (not tracked)
# Run the app - it will use Machine B's AppData settings
python run.py
```

## Key Points

✅ **local_config.py** - Machine-specific, NOT tracked by git
✅ **config.py** - Default settings, tracked by git
✅ **AppData folders** - Each machine uses its own AppData location
✅ **One-way transfers** - Just `git push` from primary machine, `git pull` on secondary

## If You Need to Change Defaults

Edit `productivity_app/app/core/config.py` to change defaults for ALL machines:

```python
APPDATA_ROOT_FOLDER = "NewDefaultName"
```

Then commit and push. Each machine can still override with `local_config.py`.
