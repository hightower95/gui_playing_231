#!/usr/bin/env python3
"""
Quick Development GUI Access
Runs the original main.py GUI for rapid development/testing
"""
import sys
import os
from pathlib import Path

# Add the gui directory to the path to import main
gui_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(gui_dir))

try:
    # Import and run the original main.py
    import main
    main.main()
except ImportError as e:
    print(f"❌ Could not import main.py: {e}")
    print(f"🔍 Looking in: {gui_dir}")
    print("💡 Make sure main.py is in the gui root directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running main.py: {e}")
    sys.exit(1)
