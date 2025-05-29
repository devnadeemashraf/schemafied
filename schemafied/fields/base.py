from abc import ABC, abstractmethod
from typing import Any, List, Callable, Optional, Union

from ..validation_context import ValidationContext
from ..exceptions import ValidationError, MissingFieldError


class Field(ABC):
    """
    Abstract base class for all field types.

    This class defines the interface that all fields must implement and provides
    common functionality for validation, type coercion, and error handling.
    """

    def __init__(
        self,
        required: bool = True,
        default: Any = None,
        validators: Optional[List[Callable[[Any], Union[bool, str]]]] = None,
        coerce: bool = True,
        description: str = "",
    ):
        """
        Initialize field with common validation parameters.

        Args:
            required: Whether this field is required
            default: Default value if field is missing or None
            validators: List of custom validator functions
            coerce: Whether to attempt type coercion
            description: Human-readable description of the field
        """
        self.required = required
        self.default = default
        self.validators = validators or []
        self.coerce = coerce
        self.description = description

    def validate(self, value: Any, context: ValidationContext) -> Any:
        """
        Main validation entry point.

        Args:
            value: Value to validate
            context: Validation context for error tracking

        Returns:
            Validated and possibly coerced value
        """
        # Handle None/missing values
        if value is None:
            return self._handle_none_value(context)

        # Perform type-specific validation
        try:
            validated_value = self._validate_type(value, context)

            # Apply custom validators if validation succeeded so far
            if not context.has_errors():
                validated_value = self._apply_custom_validators(validated_value, context)

            return validated_value

        except ValidationError as e:
            # Ensure error has proper field path
            if not e.field_path:
                e.field_path = context.field_path
            context.add_error(e)
            return value  # Return original value for continued validation

    def _handle_none_value(self, context: ValidationContext) -> Any:
        """Handle None or missing values."""
        if self.required:
            context.add_error(MissingFieldError(context.field_path))
            return self.default
        return self.default

    def _apply_custom_validators(self, value: Any, context: ValidationContext) -> Any:
        """Apply custom validator functions."""
        for validator in self.validators:
            try:
                result = validator(value)
                if result is False:
                    error = ValidationError("Custom validation failed", context.field_path)
                    context.add_error(error)
                elif isinstance(result, str):
                    # Validator returned error message
                    error = ValidationError(result, context.field_path)
                    context.add_error(error)
            except Exception as e:
                error = ValidationError(f"Validator error: {str(e)}", context.field_path)
                context.add_error(error)

        return value

    @abstractmethod
    def _validate_type(self, value: Any, context: ValidationContext) -> Any:
        """
        Type-specific validation logic.

        This method must be implemented by all field subclasses to provide
        type-specific validation and constraint checking.

        Args:
            value: Value to validate (guaranteed to be non-None)
            context: Validation context for error tracking

        Returns:
            Validated and possibly coerced value

        Raises:
            ValidationError: If validation fails
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(required={self.required})"
