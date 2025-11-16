#!/usr/bin/env python3
"""
Smart build script with git integration and multi-path watching.

Features:
- [!] Refuses to build if there are uncommitted changes
- [DIR] Watches multiple paths: source code + project config
- [TAG] Auto-increments version numbers
- [CLEAN] Cleans old builds automatically  
- 🎯 Shows exactly what changed since last build

Watched Paths:
- productivity_app/productivity_app/  (source code)
- pyproject.toml                      (project config)

Usage: 
  python package_builder.py [--minor|--major] [--no-increment]

Examples:
  python package_builder.py                    # patch version (0.1.0 → 0.1.1)
  python package_builder.py --minor            # minor version (0.1.1 → 0.2.0)
  python package_builder.py --major            # major version (0.2.0 → 1.0.0)
  python package_builder.py --no-increment     # build without version change
"""
import subprocess
import re
import sys
import os
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return output"""
    result = subprocess.run(cmd, shell=True, cwd=cwd,
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def git_has_changes_pending():
    """Check git status and refuse to build if there are uncommitted changes"""
    try:
        # Check for uncommitted changes
        status = run_command("git status --porcelain")
        if status:
            print("[ERROR] UNCOMMITTED CHANGES DETECTED!")
            print("   The following files have uncommitted changes:")
            for line in status.split('\n'):
                if line.strip():
                    print(f"     {line}")
            print("\n[!] Please commit or stash changes before building!")
            print("   Run: git add . && git commit -m 'Your commit message'")
            print("   Or:  git stash")
            return False

        print("[OK] Git working directory is clean")
        return True
    except:
        print("[WARN] Cannot check git status - make sure you're in a git repository")
        return False


def watched_paths_have_changed(watch_paths=None):
    """Check if there are changes in the watched paths since last tag"""
    if watch_paths is None:
        watch_paths = ["productivity_app/productivity_app",
                       "productivity_app/pyproject.toml"]

    try:
        # Check if watch paths exist
        existing_paths = []
        for path in watch_paths:
            if Path(path).exists():
                existing_paths.append(path)
            else:
                print(f"[WARN] Watch path '{path}' not found, skipping")

        if not existing_paths:
            print("[WARN] No valid watch paths found, assuming changes exist")
            return True

        # Check if there are commits since last tag that affect any watch path
        try:
            last_tag = run_command("git describe --tags --abbrev=0")
            all_changed_files = []

            for watch_path in existing_paths:
                commits_since = run_command(
                    f"git log {last_tag}..HEAD --oneline -- {watch_path}")
                if commits_since:
                    # Get files changed in this path
                    files_changed = run_command(
                        f"git diff --name-only {last_tag}..HEAD -- {watch_path}")
                    if files_changed:
                        path_files = [f.strip()
                                      for f in files_changed.split('\n') if f.strip()]
                        all_changed_files.extend(path_files)

            if all_changed_files:
                print(
                    f"[INFO] Found changes in watched paths since {last_tag}")
                print("   Changed files:")
                for file in sorted(set(all_changed_files)):
                    print(f"     [FILE] {file}")
                return True
            else:
                print(f"[OK] No changes in watched paths since {last_tag}")
                return False

        except:
            print(
                f"[INFO] No previous tags found, checking watched paths for any files")
            # If no tags, check if any watched paths have relevant files
            for watch_path in existing_paths:
                if Path(watch_path).is_file():
                    print(f"   Found file: {watch_path}")
                    return True
                elif Path(watch_path).is_dir():
                    source_files = list(Path(watch_path).rglob("*.py"))
                    if source_files:
                        print(
                            f"   Found {len(source_files)} Python files in '{watch_path}'")
                        return True
            return False

    except Exception as e:
        print(f"[WARN] Cannot check changes in watched paths: {e}")
        return True


def find_pyproject_toml():
    """Find pyproject.toml file"""
    # Check current directory first
    if Path("pyproject.toml").exists():
        return Path("pyproject.toml")
    # Check productivity_app subdirectory
    elif Path("productivity_app/pyproject.toml").exists():
        return Path("productivity_app/pyproject.toml")
    else:
        return None


def get_current_version():
    """Get current version from pyproject.toml"""
    pyproject_file = find_pyproject_toml()
    if not pyproject_file:
        print("[ERROR] pyproject.toml not found!")
        print("   Make sure you're running from the correct directory")
        sys.exit(1)

    content = pyproject_file.read_text()
    # Support both plain version and version with git hash
    match = re.search(
        r'version = "(\d+)\.(\d+)\.(\d+)(?:\+[a-f0-9]+)?"', content)
    if not match:
        print("[ERROR] Could not find version in pyproject.toml")
        sys.exit(1)

    return tuple(map(int, match.groups()))


def get_git_hash():
    """Get the current git commit hash"""
    try:
        return run_command("git rev-parse --short HEAD")
    except:
        print("[WARN] Could not get git hash")
        return None


def inject_git_hash_into_version():
    """Temporarily inject git hash into pyproject.toml version"""
    pyproject_file = find_pyproject_toml()
    if not pyproject_file:
        print("[ERROR] Could not find pyproject.toml!")
        return None, None

    # Read current content
    content = pyproject_file.read_text()

    # Get git hash
    git_hash = get_git_hash()
    if not git_hash:
        return content, None

    # Find current version and inject git hash
    match = re.search(r'version = "(\d+\.\d+\.\d+)(?:\+[a-f0-9]+)?"', content)
    if not match:
        print("[ERROR] Could not find version in pyproject.toml")
        return content, None

    base_version = match.group(1)
    version_with_hash = f"{base_version}+{git_hash}"

    # Replace version in content
    new_content = re.sub(
        r'version = "(\d+\.\d+\.\d+)(?:\+[a-f0-9]+)?"',
        f'version = "{version_with_hash}"',
        content
    )

    # Write the updated content
    pyproject_file.write_text(new_content)
    print(f"[INFO] Injected git hash: {base_version} -> {version_with_hash}")

    return content, version_with_hash


def restore_original_version(original_content):
    """Restore the original pyproject.toml content"""
    if original_content:
        pyproject_file = find_pyproject_toml()
        if pyproject_file:
            pyproject_file.write_text(original_content)
            print("[INFO] Restored original version in pyproject.toml")


def update_version_in_toml(version_type="patch"):
    """Update version in pyproject.toml"""
    major, minor, patch = get_current_version()

    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    # Update pyproject.toml
    pyproject_file = find_pyproject_toml()
    if not pyproject_file:
        print("[ERROR] Could not find pyproject.toml to update!")
        sys.exit(1)

    content = pyproject_file.read_text()
    # Remove any existing git hash before updating version
    content = re.sub(r'version = "(\d+\.\d+\.\d+)(?:\+[a-f0-9]+)?"',
                     r'version = "\1"', content)
    content = re.sub(r'version = "\d+\.\d+\.\d+"',
                     f'version = "{new_version}"', content)
    pyproject_file.write_text(content)

    print(f"[INFO] Updated version to {new_version}")
    return new_version


def build_package():
    """Build the package with git hash injection"""
    print("[BUILD] Building package...")

    # Find the directory containing pyproject.toml
    pyproject_file = find_pyproject_toml()
    if not pyproject_file:
        print("[ERROR] Could not find pyproject.toml!")
        sys.exit(1)

    build_dir = pyproject_file.parent
    print(f"[DIR] Building in directory: {build_dir}")

    # Inject git hash into version before building
    print("[GIT] Injecting git hash into version...")
    original_content, version_with_hash = inject_git_hash_into_version()

    try:
        # Install build tools first
        print("[PKG] Installing/upgrading build tools...")
        try:
            # Try with default PyPI index in case there are pip config issues
            run_command(
                "python -m pip install --upgrade --index-url https://pypi.org/simple build twine")
        except:
            print("[WARN] Warning: Could not upgrade build tools, continuing anyway...")

        # Remove old builds from the build directory
        print("[CLEAN] Cleaning old builds...")

        # Clean dist contents but preserve the directory
        try:
            print("[CLEAN] Cleaning dist contents...")
            run_command(
                f"python -c \"import shutil, glob, os, pathlib; os.chdir('{build_dir}'); dist_path = pathlib.Path('dist'); [os.remove(f) if f.is_file() else shutil.rmtree(f, ignore_errors=True) for f in dist_path.glob('*') if dist_path.exists()]\"")
        except:
            print(f"[WARN] Warning: Could not clean dist contents")

        # Clean build and egg-info directories completely
        for path in ["build", "*.egg-info"]:
            try:
                run_command(
                    f"python -c \"import shutil, glob, os; os.chdir('{build_dir}'); [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('{path}')]\"")
            except:
                print(f"[WARN] Warning: Could not clean {path}")

        # First, let's check if the build module is available
        print("[CHECK] Checking if build module is available...")
        try:
            result = run_command(
                "python -c \"import build; print('Build module found')\"")
            print(f"[OK] {result}")
        except:
            print("[ERROR] Build module not found!")
            print("[INFO] Installing build module...")
            try:
                # Try with default PyPI index in case there are pip config issues
                run_command(
                    "python -m pip install --index-url https://pypi.org/simple build")
                print("[OK] Build module installed")
            except Exception as install_error:
                print(
                    f"[ERROR] Could not install build module: {install_error}")
                print("[TIP] Try manually running: pip install build")
                sys.exit(1)

        # Validate pyproject.toml before building
        print(f"[VALIDATE] Checking pyproject.toml content...")
        try:
            pyproject_path = build_dir / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"[INFO] pyproject.toml exists ({len(content)} bytes)")
                    
                    # Basic check for key sections
                    if '[build-system]' in content:
                        print(f"[INFO] Found [build-system] section")
                    if '[project]' in content:
                        print(f"[INFO] Found [project] section")
                    if '[tool.setuptools' in content:
                        print(f"[INFO] Found [tool.setuptools] section")
                    
                    # Extract key values using simple text parsing
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('name = '):
                            print(f"[INFO] Project name: {line}")
                        elif line.startswith('version = '):
                            print(f"[INFO] Project version: {line}")
                        elif 'build-backend' in line:
                            print(f"[INFO] Build backend: {line}")
            else:
                print(f"[ERROR] pyproject.toml not found at {pyproject_path}")
        except Exception as e:
            print(f"[WARN] Could not validate pyproject.toml: {e}")

        # Build the package in the correct directory
        print(f"[BUILD] Running build in {build_dir}...")
        print(f"[BUILD] Build directory absolute path: {build_dir.absolute()}")

        # Let's also check what's in the build directory
        print(f"[INFO] Contents of {build_dir}:")
        try:
            import os
            for item in os.listdir(build_dir):
                item_path = build_dir / item
                item_type = "dir" if item_path.is_dir() else "file"
                print(f"  - {item} ({item_type})")
        except Exception as e:
            print(f"[WARN] Could not list directory: {e}")
        
        # Check if there are Python packages to build
        print(f"[PACKAGE-CHECK] Looking for Python packages...")
        try:
            python_dirs = []
            for item in build_dir.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    python_dirs.append(str(item.name))
            
            if python_dirs:
                print(f"[INFO] Found Python packages: {', '.join(python_dirs)}")
            else:
                print(f"[WARN] No Python packages found with __init__.py files")
                
            # Also check for setup.py
            setup_py = build_dir / "setup.py"
            if setup_py.exists():
                print(f"[INFO] Found setup.py file")
            else:
                print(f"[INFO] No setup.py file found (using pyproject.toml build)")
                
        except Exception as e:
            print(f"[WARN] Could not check for Python packages: {e}")

        print(f"[DEBUG] About to start build process...")

        try:
            # Use full path to python and be very explicit
            import sys
            python_exe = sys.executable
            print(f"[INFO] Using Python: {python_exe}")

            print(f"[DEBUG] About to run subprocess with:")
            print(f"  Command: {python_exe} -m build --verbose")
            print(f"  Working directory: {build_dir}")
            print(f"  Environment PYTHONPATH cleared")

            result = subprocess.run(
                [python_exe, "-m", "build", "--verbose"],
                cwd=str(build_dir),
                capture_output=True,
                text=True,
                # Clear PYTHONPATH to avoid conflicts
                env=dict(os.environ, PYTHONPATH="")
            )

            print(f"[DEBUG] Subprocess completed with return code: {result.returncode}")

            if result.returncode == 0:
                print("[OK] Package build command completed successfully!")
                if version_with_hash:
                    print(f"[INFO] Built with version: {version_with_hash}")
                
                # Immediately check what was created
                dist_check_dir = build_dir / "dist"
                print(f"[BUILD-RESULT] Checking for build outputs in: {dist_check_dir.absolute()}")
                if dist_check_dir.exists():
                    build_files = list(dist_check_dir.glob("*"))
                    print(f"[BUILD-RESULT] Found {len(build_files)} files immediately after build:")
                    for bf in build_files:
                        print(f"  - {bf.name} ({bf.stat().st_size} bytes)")
                else:
                    print(f"[BUILD-RESULT] No dist directory found immediately after build")
                
                # Show build output with analysis
                if result.stdout:
                    print("[INFO] Build output:")
                    stdout_lines = result.stdout.strip().split('\n')
                    
                    # Look for key indicators in the output
                    wheel_created = any('Creating' in line and '.whl' in line for line in stdout_lines)
                    sdist_created = any('Creating' in line and '.tar.gz' in line for line in stdout_lines)
                    
                    print(f"[ANALYSIS] Wheel creation detected: {wheel_created}")
                    print(f"[ANALYSIS] Source dist creation detected: {sdist_created}")
                    
                    # Print full output
                    for i, line in enumerate(stdout_lines[-50:]):  # Last 50 lines
                        print(f"  {line}")
                    
                    if len(stdout_lines) > 50:
                        print(f"  ... ({len(stdout_lines) - 50} earlier lines omitted)")
                
                if result.stderr:
                    print("[WARN] Build stderr:")
                    print(result.stderr)
            else:
                print(
                    f"[ERROR] Build failed with exit code {result.returncode}")
                if result.stderr:
                    print("[ERROR] Error details:")
                    print(result.stderr)
                if result.stdout:
                    print("[INFO] Build output:")
                    print(result.stdout)
                raise Exception(
                    f"Build failed with exit code {result.returncode}")

        except FileNotFoundError as e:
            print(f"[ERROR] Python executable not found: {e}")
            print(f"[ERROR] Attempted to use: {python_exe}")
            print("[TIP] Make sure Python is properly installed and in your PATH")
            sys.exit(1)
        except subprocess.SubprocessError as e:
            print(f"[ERROR] Subprocess execution failed: {e}")
            print(f"[ERROR] Command was: {python_exe} -m build --verbose")
            print(f"[ERROR] Working directory: {build_dir}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Build failed with unexpected error: {e}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            import traceback
            print(f"[ERROR] Traceback:")
            traceback.print_exc()
            print("[TIP] Possible solutions:")
            print("  1. Make sure you're in a virtual environment")
            print("  2. Check your pyproject.toml file is valid")
            print("  3. Try running manually: python -m build --verbose")
            raise

    finally:
        # Always restore original version, even if build fails
        print("[RESTORE] Restoring original version in pyproject.toml...")
        restore_original_version(original_content)


def main():
    """Main entry point for package builder"""
    print("[INIT] Starting package builder...")

    # Check Python environment first
    import sys
    import os
    print(f"[INFO] Python executable: {sys.executable}")
    print(f"[INFO] Python version: {sys.version}")

    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[INFO] Running in virtual environment")
    else:
        print("[INFO] Running in system Python")

    # Check current working directory
    print(f"[INFO] Current working directory: {os.getcwd()}")

    # Check if build module is available early
    try:
        import build
        print(f"[INFO] Build module version: {build.__version__}")
    except ImportError:
        print("[WARN] Build module not found - will install during build process")

    # Find pyproject.toml early
    pyproject_file = find_pyproject_toml()
    if not pyproject_file:
        print("[ERROR] Could not find pyproject.toml!")
        print(
            "[INFO] Please run this script from the project root or productivity_app directory")
        sys.exit(1)
    else:
        print(f"[INFO] Found pyproject.toml at: {pyproject_file}")

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Smart build script with git integration and version management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python package_builder.py                    # patch version (0.1.0 → 0.1.1)
  python package_builder.py --minor            # minor version (0.1.1 → 0.2.0)
  python package_builder.py --major            # major version (0.2.0 → 1.0.0)
  python package_builder.py --no-increment     # build without version change
  python package_builder.py --dev              # development mode (skip git checks)
        """
    )

    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument('--minor', action='store_true',
                               help='Increment minor version (x.Y.z)')
    version_group.add_argument('--major', action='store_true',
                               help='Increment major version (X.y.z)')

    parser.add_argument('--no-increment', action='store_true',
                        help='Build without incrementing version number')
    parser.add_argument('--dev', action='store_true',
                        help='Development mode: skip git checks and allow uncommitted changes')

    args = parser.parse_args()

    # Determine version increment type
    if args.major:
        version_type = "major"
    elif args.minor:
        version_type = "minor"
    else:
        version_type = "patch"

    no_increment = args.no_increment
    dev_mode = args.dev

    # Determine if we're running from the project root or the productivity_app directory
    script_dir = Path(__file__).parent

    # Check if we're in the productivity_app directory (pyproject.toml exists here)
    if (script_dir / "pyproject.toml").exists():
        # Running from productivity_app directory
        default_watch_paths = ["productivity_app", "pyproject.toml"]
        print("[DIR] Running from productivity_app directory")
    # Check if we're in the parent directory (productivity_app subdirectory exists)
    elif (script_dir.parent / "productivity_app" / "pyproject.toml").exists():
        # Running from parent directory
        default_watch_paths = [
            "productivity_app/productivity_app", "productivity_app/pyproject.toml"]
        print("[DIR] Running from parent directory")
    else:
        print("[ERROR] Could not determine project structure!")
        print("   Make sure you're running from either:")
        print("   - The productivity_app directory (where pyproject.toml is)")
        print("   - The parent directory (where productivity_app/ folder is)")
        sys.exit(1)

    print("[CHECK] Checking git status...")

    # First, check if git working directory is clean (skip in dev mode)
    if not dev_mode and not git_has_changes_pending():
        sys.exit(1)

    if dev_mode:
        print("[DEV] Development mode: Skipping git checks")

    print(f"[CHECK] Checking for changes in watched paths...")
    print(f"   Watching: {', '.join(default_watch_paths)}")

    # Then check if there are relevant changes in the watched paths (skip in dev mode)
    if not no_increment and not dev_mode and not watched_paths_have_changed(default_watch_paths):
        print("[SKIP] No relevant changes detected, skipping build")
        return

    if no_increment:
        print("[GO] Building with current version (no increment)...")
        # Get current version without incrementing
        major, minor, patch = get_current_version()
        new_version = f"{major}.{minor}.{patch}"
    else:
        print(f"[GO] Building new {version_type} version...")
        # Update version
        new_version = update_version_in_toml(version_type)

    # Build package
    build_package()

    # Show what was built
    pyproject_file = find_pyproject_toml()
    build_dir = pyproject_file.parent if pyproject_file else Path(".")
    dist_dir = build_dir / "dist"

    print(f"[INFO] Looking for dist directory at: {dist_dir.absolute()}")

    if dist_dir.exists():
        dist_files = list(dist_dir.glob("*"))
        print(f"\n[OK] Built {len(dist_files)} files:")
        for file in dist_files:
            print(f"   [PKG] {file.name}")
    else:
        # Try alternative locations
        alternative_locations = [
            Path("dist"),
            Path("./dist"),
            Path("../dist"),
            build_dir / "dist"
        ]

        found_dist = None
        for alt_dist in alternative_locations:
            if alt_dist.exists() and alt_dist.is_dir():
                found_dist = alt_dist
                break

        if found_dist:
            dist_files = list(found_dist.glob("*"))
            print(f"\n[OK] Found dist directory at: {found_dist.absolute()}")
            print(f"[OK] Built {len(dist_files)} files:")
            for file in dist_files:
                print(f"   [PKG] {file.name}")
        else:
            print(f"\n[WARN] No dist directory found!")
            print(f"[INFO] Searched locations:")
            for alt_dist in alternative_locations:
                print(
                    f"  - {alt_dist.absolute()} (exists: {alt_dist.exists()})")

            # List current directory contents for debugging
            print(
                f"[DEBUG] Contents of build directory ({build_dir.absolute()}):")
            try:
                for item in build_dir.iterdir():
                    print(
                        f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
            except Exception as e:
                print(f"  Error listing directory: {e}")

    print(f"\n[DONE] Build complete! Version: {new_version}")
    print("\nNext steps:")
    print("  - Test your package: pip install dist/*.whl")

    if no_increment:
        print("  - Version unchanged - no commit needed for version")
    else:
        print("  - Commit version bump: git add . && git commit -m 'Bump version to {}'".format(new_version))

    print("  - Tag release: git tag v{}".format(new_version))
    print("  - Push: git push && git push --tags")


if __name__ == "__main__":
    main()
