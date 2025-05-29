#!/usr/bin/env python3
"""Upload start messages."""

import sys
import re


def get_version():
    """Get version from __init__.py"""
    with open("schemafied/__init__.py", "r") as f:
        content = f.read()
    version_match = re.search(r'__version__ = ["\']([^"\']*)["\']', content)
    return version_match.group(1) if version_match else "unknown"


def main():
    upload_type = sys.argv[1] if len(sys.argv) > 1 else "prod"
    version = get_version()

    if upload_type == "test":
        print(f"🚀 Uploading schemafied v{version} to test PyPI...")
    else:
        print(f"🚀 Uploading schemafied v{version} to production PyPI...")


if __name__ == "__main__":
    main()
