"""
Version management utilities
Pure functions for version parsing, comparison, and upgrade logic
"""
import re
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Tuple


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse semantic version string into (major, minor, patch)"""
    try:
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except Exception:
        pass
    return (0, 0, 0)


def is_stable_version(version_str: str) -> bool:
    """Check if version is stable (even minor version)"""
    major, minor, patch = parse_version(version_str)
    return minor % 2 == 0


def get_installed_version(venv_python: Path, library_name: str) -> Optional[str]:
    """Get currently installed library version"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "show", library_name],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return None


def get_all_versions(venv_python: Path, library_name: str) -> List[str]:
    """Get all available versions from PyPI"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "index", "versions", library_name],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            versions = []
            for line in result.stdout.split('\n'):
                # Parse pip index output format
                if 'Available versions:' in line:
                    version_part = line.split('Available versions:', 1)[1]
                    versions = [v.strip()
                                for v in version_part.split(',') if v.strip()]
                    break
            return versions
    except Exception:
        pass
    return []


def get_latest_stable_version(venv_python: Path, library_name: str) -> Optional[str]:
    """Get the latest stable version of a library"""
    all_versions = get_all_versions(venv_python, library_name)
    stable_versions = [v for v in all_versions if is_stable_version(v)]

    if stable_versions:
        # Sort versions and return latest
        sorted_versions = sorted(
            stable_versions, key=parse_version, reverse=True)
        return sorted_versions[0]

    return None


def detect_local_index(venv_python: Path, library_name: str) -> bool:
    """Detect if library was installed from local index-url"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "show", library_name],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            # Look for local file paths or custom URLs in the output
            for line in result.stdout.split('\n'):
                if line.startswith('Location:'):
                    location = line.split(':', 1)[1].strip()
                    # Check if it's a local path or non-PyPI URL
                    if 'site-packages' not in location or 'file:///' in location:
                        return True
                elif line.startswith('Home-page:') or line.startswith('Download-URL:'):
                    url = line.split(':', 1)[1].strip()
                    if url and not url.startswith('https://pypi.org'):
                        return True
    except Exception:
        pass
    return False


def should_upgrade(current_version: str, config: Dict[str, bool], venv_python: Path, library_name: str) -> Optional[str]:
    """Determine if and to which version we should upgrade using granular controls"""
    current_major, current_minor, current_patch = parse_version(
        current_version)
    allow_test_releases = config.get('allow_upgrade_to_test_releases', False)

    # Get upgrade permissions
    auto_upgrade_major = config.get('auto_upgrade_major_version', False)
    auto_upgrade_minor = config.get('auto_upgrade_minor_version', False)
    auto_upgrade_patches = config.get('auto_upgrade_patches', False)

    # If no upgrades are enabled, skip
    if not (auto_upgrade_major or auto_upgrade_minor or auto_upgrade_patches):
        return None

    # Get all available versions
    all_versions = get_all_versions(venv_python, library_name)
    candidate_versions = []

    for version in all_versions:
        major, minor, patch = parse_version(version)

        # Skip if it's a test release and not allowed
        if not allow_test_releases and not is_stable_version(version):
            continue

        # Determine upgrade type needed
        if major > current_major:
            # Major version upgrade
            if auto_upgrade_major:
                candidate_versions.append(
                    (version, major, minor, patch, 'major'))
        elif major == current_major and minor > current_minor:
            # Minor version upgrade within same major
            if auto_upgrade_minor:
                candidate_versions.append(
                    (version, major, minor, patch, 'minor'))
        elif major == current_major and minor == current_minor and patch > current_patch:
            # Patch version upgrade within same minor
            if auto_upgrade_patches:
                candidate_versions.append(
                    (version, major, minor, patch, 'patch'))

    # If we have candidates, return the latest one
    if candidate_versions:
        # Sort by version tuple and return latest
        candidate_versions.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)
        return candidate_versions[0][0]

    return None


def upgrade_to_version(venv_python: Path, library_name: str, target_version: str) -> bool:
    """Upgrade to specific version"""
    try:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install",
             library_name + "==" + target_version],
            capture_output=True, text=True, timeout=300
        )
        return result.returncode == 0
    except Exception:
        return False
