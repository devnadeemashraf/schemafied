#!/usr/bin/env python3
"""Version verification script for pyproject.toml build system."""

import sys
import re
import os


def get_version_from_init():
    """Extract version from schemafied/__init__.py"""
    try:
        with open("schemafied/__init__.py", "r") as f:
            init_content = f.read()

        version_match = re.search(r'__version__ = ["\']([^"\']*)["\']', init_content)
        if version_match:
            return version_match.group(1)
        else:
            raise RuntimeError(
                "Unable to find version string in schemafied/__init__.py"
            )

    except Exception as e:
        raise RuntimeError(f"Cannot extract version from __init__.py: {e}")


def test_dynamic_version_import():
    """Test that the pyproject.toml dynamic configuration actually works by importing."""
    try:
        # Add the current directory to Python path so schemafied package is importable
        import sys
        import os

        # Get the project root directory (where schemafied/ folder exists)
        project_root = os.getcwd()
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        # Now test the exact import path that pyproject.toml uses
        import schemafied

        return schemafied.__version__
    except ImportError as e:
        raise RuntimeError(f"Cannot import schemafied package: {e}")
    except AttributeError as e:
        raise RuntimeError(f"schemafied package has no __version__ attribute: {e}")


def verify_pyproject_config():
    """Verify pyproject.toml has correct dynamic version configuration."""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()

        # Check for dynamic version declaration
        if 'dynamic = ["version"]' not in content:
            raise RuntimeError("pyproject.toml missing dynamic version declaration")

        # Check for setuptools dynamic configuration
        if 'version = { attr = "schemafied.__version__" }' not in content:
            raise RuntimeError(
                "pyproject.toml missing setuptools dynamic version config"
            )

        return True
    except FileNotFoundError:
        raise RuntimeError("pyproject.toml not found")


def main():
    print("🔄 Checking version configuration...")

    # Check if __init__.py exists and has version
    if not os.path.exists("schemafied/__init__.py"):
        print("❌ schemafied/__init__.py not found")
        sys.exit(1)

    # Get version from single source of truth
    version = get_version_from_init()
    print(f"📦 Package version: {version}")

    # Verify version format (semantic versioning)
    if not re.match(r"^\d+\.\d+\.\d+", version):
        print(f"❌ Invalid version format: {version}")
        print("   Expected format: X.Y.Z (semantic versioning)")
        sys.exit(1)

    # Verify pyproject.toml configuration
    try:
        verify_pyproject_config()
        print("✅ pyproject.toml configuration verified")
    except Exception as e:
        print(f"❌ pyproject.toml configuration error: {e}")
        sys.exit(1)

    # Test that the dynamic import actually works (the critical test)
    try:
        imported_version = test_dynamic_version_import()
        if imported_version != version:
            print(
                f"❌ Version mismatch: __init__.py has '{version}', import reads '{imported_version}'"
            )
            sys.exit(1)
        print(f"✅ Dynamic version import works: {imported_version}")
    except Exception as e:
        print(f"❌ Dynamic version import failed: {e}")
        print("   This means pyproject.toml cannot read your version during build")
        sys.exit(1)

    print("✅ Version configuration verification passed")
    print("🎉 Your pyproject.toml setup is working correctly!")


if __name__ == "__main__":
    main()
