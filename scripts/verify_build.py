#!/usr/bin/env python3
"""Build verification script."""

import os
import sys
import zipfile
import re


def get_version():
    """Get version from __init__.py"""
    with open("schemafied/__init__.py", "r") as f:
        content = f.read()
    version_match = re.search(r'__version__ = ["\']([^"\']*)["\']', content)
    if not version_match:
        print("❌ Cannot determine expected version")
        sys.exit(1)
    return version_match.group(1)


def verify_build_system():
    """Verify that build artifacts were created using pyproject.toml"""
    if os.path.exists("setup.py"):
        print("⚠️  Warning: setup.py still exists - ensure build used pyproject.toml")

    if not os.path.exists("pyproject.toml"):
        print("❌ pyproject.toml not found - build system misconfiguration")
        sys.exit(1)

    print("✅ Build system configuration verified")


def main():
    """Main function to verify build artifacts."""
    print("🔍 Verifying build artifacts...")
    verify_build_system()

    # Check if dist directory exists
    if not os.path.exists("dist"):
        print("❌ dist/ directory not found. Run `make build` first.")
        sys.exit(1)

    expected_version = get_version()
    print(f"📦 Expected version: {expected_version}")

    # List dist contents
    dist_files = os.listdir("dist")
    print(f"📁 Found {len(dist_files)} files in dist/:")
    for f in dist_files:
        print(f"   - {f}")

    # Check for expected files
    expected_wheel = f"schemafied-{expected_version}-py3-none-any.whl"
    expected_sdist = f"schemafied-{expected_version}.tar.gz"

    if expected_wheel not in dist_files:
        print(f"❌ Expected wheel not found: {expected_wheel}")
        sys.exit(1)
    print(f"✅ Found wheel: {expected_wheel}")

    if expected_sdist not in dist_files:
        print(f"❌ Expected source distribution not found: {expected_sdist}")
        sys.exit(1)
    print(f"✅ Found source distribution: {expected_sdist}")

    # Verify wheel contents
    wheel_path = os.path.join("dist", expected_wheel)
    try:
        with zipfile.ZipFile(wheel_path, "r") as zf:
            files = zf.namelist()

            # Check for METADATA file
            metadata_files = [f for f in files if "METADATA" in f]
            if not metadata_files:
                print("❌ No METADATA file found in wheel")
                sys.exit(1)

            # Read and verify metadata
            with zf.open(metadata_files[0]) as mf:
                metadata = mf.read().decode("utf-8")

                # Check version in metadata
                version_line = [
                    line for line in metadata.split("\n") if line.startswith("Version:")
                ]
                if not version_line:
                    print("❌ No Version line found in METADATA")
                    sys.exit(1)

                metadata_version = version_line[0].split(":", 1)[1].strip()
                if metadata_version != expected_version:
                    print(
                        f"❌ Version mismatch in wheel metadata: expected {expected_version}, got {metadata_version}"
                    )
                    sys.exit(1)

                print(f"✅ Wheel metadata version: {metadata_version}")

                # Check package name
                name_line = [
                    line for line in metadata.split("\n") if line.startswith("Name:")
                ]
                if name_line:
                    package_name = name_line[0].split(":", 1)[1].strip()
                    print(f"✅ Package name: {package_name}")
    except Exception as e:
        print(f"❌ Error reading wheel: {e}")
        sys.exit(1)

    print("✅ Build verification passed")


if __name__ == "__main__":
    main()
