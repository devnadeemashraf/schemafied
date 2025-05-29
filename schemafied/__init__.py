"""
Schemafied - A Python library for validating data structures against user-defined schemas.

This library provides comprehensive dictionary validation with support for:
- Nested structures (dictionaries and lists)
- Custom field types and validators
- Detailed error reporting with field paths
- Type coercion and default values
- Performance optimization for large datasets
"""

__version__ = "1.0.0"
__author__ = "Nadeem Ashraf"
__email__ = "dev.nadeemashraf06@gmail.com"
__license__ = "MIT"

# Core exports
from .schema import Schema
from .exceptions import (
    ValidationError,
    ValidationErrorCollection,
    MissingFieldError,
    ConstraintError,
    TypeValidationError,
    NestedValidationError,
)

# Field exports
from .fields import (
    Field,
    NumberField,
    StringField,
    ListField,
    DictField,
)

# Validation context (advanced usage)
from .validation_context import ValidationContext

# No TYPE_CHECKING section needed - everything available everywhere

__all__ = [
    # Core classes
    "Schema",
    "ValidationContext",
    # Field types
    "Field",
    "NumberField",
    "StringField",
    "ListField",
    "DictField",
    # Exceptions
    "ValidationError",
    "ValidationErrorCollection",
    "MissingFieldError",
    "ConstraintError",
    "TypeValidationError",
    "NestedValidationError",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
