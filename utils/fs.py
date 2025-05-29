def read_file(path: str) -> str:
    """Read a file at a specified path and return it's content."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {path}")
    except IOError as e:
        raise RuntimeError(f"Error reading file {path}: {e}")
