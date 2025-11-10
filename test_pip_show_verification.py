"""
Test script to demonstrate the pip show pip verification logic
This replicates what happens in the venv_step.py _test_existing_venv method
"""
import subprocess
import sys
from pathlib import Path

def test_venv_verification():
    """Test the exact same verification logic used in the installer"""
    
    # Path to the virtual environment that was created
    venv_path = Path(r"c:\Users\peter\OneDrive\Documents\Coding\gui\alternative_app_installer\.test_venv")
    installation_path = r"c:\Users\peter\OneDrive\Documents\Coding\gui\alternative_app_installer"
    
    print("🔍 Testing Virtual Environment Verification Logic")
    print("=" * 50)
    print(f"📁 Virtual environment path: {venv_path}")
    print(f"📂 Installation path: {installation_path}")
    print()
    
    # Step 1: Check if venv directory exists
    if not venv_path.exists():
        print("❌ Virtual environment directory not found")
        return False
    
    print("✅ Virtual environment directory found")
    
    # Step 2: Check for python executable
    if sys.platform.startswith('win'):
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        venv_python = venv_path / "bin" / "python"
    
    print(f"🐍 Looking for python executable: {venv_python}")
    
    if not venv_python.exists():
        print("❌ Virtual environment python executable not found")
        return False
        
    print("✅ Virtual environment python executable found")
    
    # Step 3: Run pip show pip (the actual verification test)
    print("\n🧪 Running 'pip show pip' to test venv functionality...")
    print("▶️ Command:", f'{str(venv_python)} -m pip show pip')
    print("-" * 40)
    
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "show", "pip"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=installation_path
        )
        
        print("📊 Return code:", result.returncode)
        print("\n📝 STDOUT Output:")
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ STDERR Output:")
            print(result.stderr)
        
        # The verification logic
        success = result.returncode == 0 and "Name: pip" in result.stdout
        
        print("\n🔍 Verification Logic:")
        print(f"   - Return code == 0: {result.returncode == 0}")
        print(f"   - Contains 'Name: pip': {'Name: pip' in result.stdout}")
        print(f"   - Overall success: {success}")
        
        if success:
            print("\n✅ Virtual environment pip test successful!")
            print("🎉 This virtual environment is fully functional!")
            return True
        else:
            print("\n❌ Virtual environment pip test failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Virtual environment test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing virtual environment: {e}")
        return False

if __name__ == "__main__":
    test_venv_verification()