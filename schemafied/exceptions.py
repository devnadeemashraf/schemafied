from typing import List, Dict, Any


class ValidationError(Exception):
    """Base validation error with structured error information."""

    def __init__(
        self,
        message: str,
        field_path: str = "",
        error_code: str = "validation_error",
        value: Any = None,
    ):
        super().__init__(message)
        self.message = message
        self.field_path = field_path
        self.error_code = error_code
        self.value = value

    def __str__(self):
        if self.field_path:
            return f"{self.field_path}: {self.message}"
        return self.message

    def __repr__(self):
        return f"ValidationError(message='{self.message}', field_path='{self.field_path}')"


class ValidationErrorCollection(Exception):
    """Collection of validation errors with structured reporting."""

    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        super().__init__(self._format_errors())

    def _format_errors(self) -> str:
        """Format all errors into a readable string."""
        if not self.errors:
            return "No validation errors"

        # Group errors by field path for cleaner output
        grouped_errors = self._group_errors_by_field()

        error_lines = []
        for field_path, field_errors in grouped_errors.items():
            messages = [error.message for error in field_errors]
            if len(messages) == 1:
                error_lines.append(f"{field_path}: {messages[0]}")
            else:
                error_lines.append(f"{field_path}: {'; '.join(messages)}")

        return "Validation failed:\n  " + "\n  ".join(error_lines)

    def _group_errors_by_field(self) -> Dict[str, List[ValidationError]]:
        """Group errors by field path."""
        grouped = {}
        for error in self.errors:
            field_path = error.field_path or "root"
            if field_path not in grouped:
                grouped[field_path] = []
            grouped[field_path].append(error)
        return grouped

    def get_errors_by_field(self) -> Dict[str, List[ValidationError]]:
        """Get errors grouped by field path."""
        return self._group_errors_by_field()

    def has_field_errors(self, field_path: str) -> bool:
        """Check if a specific field has errors."""
        return any(error.field_path == field_path for error in self.errors)

    def get_field_errors(self, field_path: str) -> List[ValidationError]:
        """Get all errors for a specific field path."""
        return [error for error in self.errors if error.field_path == field_path]


# Specific error types
class MissingFieldError(ValidationError):
    """Error for missing required fields."""

    def __init__(self, field_path: str):
        super().__init__("This field is required", field_path, "required")


class ConstraintError(ValidationError):
    """Error for constraint violations."""

    def __init__(self, field_path: str, constraint: str, value: Any = None):
        super().__init__(constraint, field_path, "constraint", value)


class TypeValidationError(ValidationError):
    """Error for type validation failures."""

    def __init__(self, field_path: str, expected_type: str, actual_type: str, value: Any = None):
        message = f"Expected {expected_type}, got {actual_type}"
        super().__init__(message, field_path, "type_error", value)
        self.expected_type = expected_type
        self.actual_type = actual_type


class NestedValidationError(ValidationError):
    """Error for nested validation failures."""

    def __init__(self, field_path: str, nested_errors: List[ValidationError]):
        error_count = len(nested_errors)
        message = f"Nested validation failed with {error_count} errors"
        super().__init__(message, field_path, "nested_validation")
        self.nested_errors = nested_errors
