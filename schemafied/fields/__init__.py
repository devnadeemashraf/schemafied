"""
Field definitions for the schemafied validation library.

This module contains all the built-in field types that can be used
to construct validation schemas.
"""

# Import Annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Field
    from .number import NumberField
    from .string import StringField
    from .list import ListField
    from .dict import DictField

# Export only the field types, not the base class
__all__: list[str] = [
    "Field",
    "NumberField",
    "StringField",
    "ListField",
    "DictField",
]
