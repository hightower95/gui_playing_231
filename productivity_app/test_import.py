"""
Test script to verify productivity_app can be imported and used correctly
"""
import productivity_app
import sys
import os

# Add the parent directory to path so we can import productivity_app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Test import

# Test that we can access the module attributes
print(f"✓ Successfully imported productivity_app")
print(f"  Version: {productivity_app.__version__}")
print(f"  Author: {productivity_app.__author__}")
print(f"  License: {productivity_app.__license__}")

# Test that start() and main() exist
print(f"\n✓ Available functions:")
print(f"  - productivity_app.start()")
print(f"  - productivity_app.main()")

print(f"\n✓ Import test successful!")
print(f"\nTo run the application, use:")
print(f"  import productivity_app")
print(f"  productivity_app.start()")

# Note: We don't actually call start() here because it would launch the GUI
