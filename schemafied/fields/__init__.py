"""
Field definitions for the schemafied validation library.

This module contains all the built-in field types that can be used
to construct validation schemas.
"""

from .base import Field
from .number import NumberField
from .string import StringField
from .list import ListField
from .dict import DictField

# Export only the field types, not the base class
__all__ = [
    "Field",
    "NumberField",
    "StringField",
    "ListField",
    "DictField",
]
