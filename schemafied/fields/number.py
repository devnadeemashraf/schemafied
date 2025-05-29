from typing import Any, Union, Optional

from .base import Field
from ..validation_context import ValidationContext
from ..exceptions import ConstraintError, TypeValidationError


class NumberField(Field):
    """
    Field for validating numeric values (int or float).

    Supports min/max constraints and automatic type coercion from strings.
    """

    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        **kwargs,
    ) -> None:
        """
        Initialize NumberField with constraints.

        Args:
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            **kwargs: Additional field parameters
        """
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def _validate_type(self, value: Any, context: ValidationContext) -> Union[int, float]:
        """Validate and coerce numeric values."""
        # Type validation with coercion
        if not isinstance(value, (int, float)):
            if self.coerce and isinstance(value, str):
                coerced_value = self._coerce_from_string(value, context)
                if coerced_value is None:
                    return value  # Error already added to context
                value = coerced_value
            else:
                error = TypeValidationError(context.field_path, "number", type(value).__name__, value)
                context.add_error(error)
                return value

        # Constraint validation
        self._validate_constraints(value, context)

        return value

    def _coerce_from_string(self, value: str, context: ValidationContext) -> Optional[Union[int, float]]:
        """Attempt to coerce string to number."""
        try:
            # Try int first, then float
            if "." in value or "e" in value.lower():
                return float(value)
            else:
                return int(value)
        except ValueError:
            error = TypeValidationError(context.field_path, "number", "string (non-numeric)", value)
            context.add_error(error)
            return None

    def _validate_constraints(self, value: Union[int, float], context: ValidationContext) -> None:
        """Validate numeric constraints."""
        if self.min_value is not None and value < self.min_value:
            if self.max_value is not None:
                constraint = f"must be between {self.min_value} and {self.max_value}"
            else:
                constraint = f"must be at least {self.min_value}"
            context.add_error(ConstraintError(context.field_path, constraint, value))

        if self.max_value is not None and value > self.max_value:
            if self.min_value is not None:
                constraint = f"must be between {self.min_value} and {self.max_value}"
            else:
                constraint = f"must be at most {self.max_value}"
            context.add_error(ConstraintError(context.field_path, constraint, value))

    def __repr__(self) -> str:
        constraints = []
        if self.min_value is not None:
            constraints.append(f"min={self.min_value}")
        if self.max_value is not None:
            constraints.append(f"max={self.max_value}")

        constraint_str = f"({', '.join(constraints)})" if constraints else ""
        return f"NumberField{constraint_str}"
