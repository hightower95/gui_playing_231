#!/usr/bin/env python3
"""
Smart build script with git integration and multi-path watching.

Features:
- 🚨 Refuses to build if there are uncommitted changes
- 📁 Watches multiple paths: source code + project config
- 🏷️ Auto-increments version numbers
- 🧹 Cleans old builds automatically  
- 🎯 Shows exactly what changed since last build

Watched Paths:
- productivity_app/productivity_app/  (source code)
- pyproject.toml                      (project config)

Usage: 
  python build.py [patch|minor|major]

Examples:
  python build.py                    # patch version (0.1.0 → 0.1.1)
  python build.py minor              # minor version (0.1.1 → 0.2.0)
  python build.py major              # major version (0.2.0 → 1.0.0)
"""
import subprocess
import re
import sys
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
            print("❌ UNCOMMITTED CHANGES DETECTED!")
            print("   The following files have uncommitted changes:")
            for line in status.split('\n'):
                if line.strip():
                    print(f"     {line}")
            print("\n🚨 Please commit or stash changes before building!")
            print("   Run: git add . && git commit -m 'Your commit message'")
            print("   Or:  git stash")
            return False

        print("✅ Git working directory is clean")
        return True
    except:
        print("⚠️ Cannot check git status - make sure you're in a git repository")
        return False


def watched_paths_have_changed(watch_paths=None):
    """Check if there are changes in the watched paths since last tag"""
    if watch_paths is None:
        watch_paths = ["productivity_app/productivity_app", "pyproject.toml"]

    try:
        # Check if watch paths exist
        existing_paths = []
        for path in watch_paths:
            if Path(path).exists():
                existing_paths.append(path)
            else:
                print(f"⚠️ Watch path '{path}' not found, skipping")

        if not existing_paths:
            print("⚠️ No valid watch paths found, assuming changes exist")
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
                print(f"📝 Found changes in watched paths since {last_tag}")
                print("   Changed files:")
                for file in sorted(set(all_changed_files)):
                    print(f"     📄 {file}")
                return True
            else:
                print(f"✅ No changes in watched paths since {last_tag}")
                return False

        except:
            print(f"📝 No previous tags found, checking watched paths for any files")
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
        print(f"⚠️ Cannot check changes in watched paths: {e}")
        return True


def get_current_version():
    """Get current version from pyproject.toml"""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print("❌ pyproject.toml not found!")
        sys.exit(1)

    content = pyproject_file.read_text()
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        print("❌ Could not find version in pyproject.toml")
        sys.exit(1)

    return tuple(map(int, match.groups()))


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
    pyproject_file = Path("pyproject.toml")
    content = pyproject_file.read_text()
    content = re.sub(r'version = "\d+\.\d+\.\d+"',
                     f'version = "{new_version}"', content)
    pyproject_file.write_text(content)

    print(f"📝 Updated version to {new_version}")
    return new_version


def build_package():
    """Build the package"""
    print("🏗️ Building package...")

    # Clean previous builds
    run_command("python -m pip install --upgrade build twine")

    # Remove old builds
    for path in ["dist", "build", "*.egg-info"]:
        run_command(
            f"python -c \"import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('{path}')]\"")

    # Build
    run_command("python -m build")
    print("✅ Package built successfully!")


def main():
    version_type = sys.argv[1] if len(sys.argv) > 1 else "patch"

    # Default watch paths: source code + project config
    default_watch_paths = [
        "productivity_app/productivity_app", "pyproject.toml"]

    if version_type not in ["patch", "minor", "major"]:
        print("Usage: python build.py [patch|minor|major]")
        print("Examples:")
        print("  python build.py                           # patch version")
        print("  python build.py minor                     # minor version")
        print("  python build.py major                     # major version")
        print(f"\nWatched paths: {', '.join(default_watch_paths)}")
        sys.exit(1)

    print("🔍 Checking git status...")

    # First, check if git working directory is clean
    if not git_has_changes_pending():
        sys.exit(1)

    print(f"🔍 Checking for changes in watched paths...")
    print(f"   Watching: {', '.join(default_watch_paths)}")

    # Then check if there are relevant changes in the watched paths
    if not watched_paths_have_changed(default_watch_paths):
        print("⏭️ No relevant changes detected, skipping build")
        return

    print(f"🚀 Building new {version_type} version...")

    # Update version
    new_version = update_version_in_toml(version_type)

    # Build package
    build_package()

    # Show what was built
    dist_files = list(Path("dist").glob("*"))
    print(f"\n✅ Built {len(dist_files)} files:")
    for file in dist_files:
        print(f"   📦 {file.name}")

    print(f"\n🎉 Build complete! Version: {new_version}")
    print("\nNext steps:")
    print("  - Test your package: pip install dist/*.whl")
    print("  - Commit version bump: git add . && git commit -m 'Bump version to {}'".format(new_version))
    print("  - Tag release: git tag v{}".format(new_version))
    print("  - Push: git push && git push --tags")


if __name__ == "__main__":
    main()
