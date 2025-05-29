from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Container for validation results with error tracking."""

    value: Any
    is_valid: bool
    errors: List["ValidationError"] = None  # type: ignore

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ValidationContext:
    """
    Context manager for validation operations with hierarchical error tracking.

    This class manages the validation state and provides clean error aggregation
    for nested data structures.
    """

    def __init__(self, field_path: str = "", parent: Optional["ValidationContext"] = None):
        self.field_path = field_path
        self.parent = parent
        self.errors: List["ValidationError"] = []  # type: ignore
        self._children: List["ValidationContext"] = []

    def create_child(self, field_name: str) -> "ValidationContext":
        """
        Create a child context for nested field validation.

        Args:
            field_name: Name of the nested field

        Returns:
            New ValidationContext with proper field path
        """
        child_path = self._build_field_path(field_name)
        child = ValidationContext(field_path=child_path, parent=self)
        self._children.append(child)
        return child

    def _build_field_path(self, field_name: str) -> str:
        """Build hierarchical field path for error reporting."""
        if not self.field_path:
            return field_name

        # Handle array indices
        if field_name.startswith("[") and field_name.endswith("]"):
            return f"{self.field_path}{field_name}"

        return f"{self.field_path}.{field_name}"

    def add_error(self, error: "ValidationError") -> None:  # type: ignore
        """
        Add a validation error to this context.

        Args:
            error: ValidationError instance
        """
        # Ensure error has proper field path
        if not error.field_path:
            error.field_path = self.field_path

        self.errors.append(error)

    def collect_all_errors(self) -> List["ValidationError"]:  # type: ignore
        """
        Collect all errors from this context and all child contexts.

        Returns:
            List of all validation errors in the hierarchy
        """
        all_errors = self.errors.copy()

        for child in self._children:
            all_errors.extend(child.collect_all_errors())

        return all_errors

    def has_errors(self) -> bool:
        """Check if this context or any child context has errors."""
        if self.errors:
            return True

        return any(child.has_errors() for child in self._children)

    def get_error_summary(self) -> Dict[str, List[str]]:
        """
        Get a summary of errors grouped by field path.

        Returns:
            Dictionary mapping field paths to error messages
        """
        all_errors = self.collect_all_errors()
        summary = {}

        for error in all_errors:
            field_path = error.field_path or "root"
            if field_path not in summary:
                summary[field_path] = []
            summary[field_path].append(error.message)

        return summary

    def clear_errors(self) -> None:
        """Clear all errors from this context and children."""
        self.errors.clear()
        for child in self._children:
            child.clear_errors()

    def __str__(self) -> str:
        """String representation showing field path and error count."""
        error_count = len(self.collect_all_errors())
        return f"ValidationContext(path='{self.field_path}', errors={error_count})"
