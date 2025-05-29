from typing import Any, Optional, Pattern, Union
import re

from .base import Field
from ..validation_context import ValidationContext
from ..exceptions import ConstraintError, TypeValidationError


class StringField(Field):
    """
    Field for validating string values.

    Supports length constraints, regex patterns, and automatic type coercion.
    """

    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[Union[str, Pattern]] = None,
        **kwargs,
    ):
        """
        Initialize StringField with constraints.

        Args:
            min_length: Minimum string length (inclusive)
            max_length: Maximum string length (inclusive)
            pattern: Regex pattern that the string must match
            **kwargs: Additional field parameters
        """
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = self._compile_pattern(pattern) if pattern else None

    def _compile_pattern(self, pattern: Union[str, Pattern]) -> Pattern:
        """Compile regex pattern if it's a string."""
        if isinstance(pattern, str):
            try:
                return re.compile(pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return pattern

    def _validate_type(self, value: Any, context: ValidationContext) -> str:
        """Validate and coerce string values."""
        # Type validation with coercion
        if not isinstance(value, str):
            if self.coerce:
                try:
                    value = str(value)
                except Exception:
                    error = TypeValidationError(context.field_path, "string", type(value).__name__, value)
                    context.add_error(error)
                    return value
            else:
                error = TypeValidationError(context.field_path, "string", type(value).__name__, value)
                context.add_error(error)
                return value

        # Constraint validation
        self._validate_constraints(value, context)

        return value

    def _validate_constraints(self, value: str, context: ValidationContext) -> None:
        """Validate string constraints."""
        # Length constraints
        value_length = len(value)

        if self.min_length is not None and value_length < self.min_length:
            if self.max_length is not None:
                constraint = f"length must be between {self.min_length} and {self.max_length} characters"
            else:
                constraint = f"must be at least {self.min_length} characters long"
            context.add_error(ConstraintError(context.field_path, constraint, value))

        if self.max_length is not None and value_length > self.max_length:
            if self.min_length is not None:
                constraint = f"length must be between {self.min_length} and {self.max_length} characters"
            else:
                constraint = f"must be at most {self.max_length} characters long"
            context.add_error(ConstraintError(context.field_path, constraint, value))

        # Pattern constraint
        if self.pattern and not self.pattern.match(value):
            constraint = f"must match pattern: {self.pattern.pattern}"
            context.add_error(ConstraintError(context.field_path, constraint, value))

    def __repr__(self):
        constraints = []
        if self.min_length is not None:
            constraints.append(f"min_length={self.min_length}")
        if self.max_length is not None:
            constraints.append(f"max_length={self.max_length}")
        if self.pattern:
            constraints.append(f"pattern='{self.pattern.pattern}'")

        constraint_str = f"({', '.join(constraints)})" if constraints else ""
        return f"StringField{constraint_str}"
