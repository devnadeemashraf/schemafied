#!/usr/bin/env python3
"""Release completion information."""

import re


def get_version():
    """Get version from __init__.py"""
    with open("schemafied/__init__.py", "r") as f:
        content = f.read()
    version_match = re.search(r'__version__ = ["\']([^"\']*)["\']', content)
    return version_match.group(1) if version_match else "unknown"


def main():
    version = get_version()

    print(f"📦 schemafied v{version} is now available on PyPI!")
    print("")
    print("Next steps:")
    print(f'1. Create GitHub tag: git tag -a v{version} -m "Release {version}"')
    print(f"2. Push tag: git push origin v{version}")
    print("3. Create GitHub release from tag")
    print(f"4. Test installation: pip install schemafied=={version}")
    print("5. Update documentation if needed")


if __name__ == "__main__":
    main()
