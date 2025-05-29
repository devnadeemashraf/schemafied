from typing import Any, List as ListType, Optional

from .base import Field
from ..validation_context import ValidationContext
from ..exceptions import ValidationError, ConstraintError, TypeValidationError


class ListField(Field):
    """
    Field for validating lists with item type validation.

    Validates that the value is a list and that all items conform to the
    specified item field type.
    """

    def __init__(
        self,
        item_field: Field,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        max_item_errors: int = 10,
        **kwargs,
    ) -> None:
        """
        Initialize ListField with item validation.

        Args:
            item_field: Field instance for validating list items
            min_length: Minimum list length (inclusive)
            max_length: Maximum list length (inclusive)
            max_item_errors: Maximum number of item errors to report
            **kwargs: Additional field parameters
        """
        super().__init__(**kwargs)
        self.item_field = item_field
        self.min_length = min_length
        self.max_length = max_length
        self.max_item_errors = max_item_errors

    def _validate_type(self, value: Any, context: ValidationContext) -> ListType[Any]:
        """Validate list type and contents."""
        # Type validation with coercion
        if not isinstance(value, list):
            if self.coerce and hasattr(value, "__iter__") and not isinstance(value, (str, dict)):
                try:
                    value = list(value)
                except (TypeError, ValueError):
                    error = TypeValidationError(context.field_path, "list", type(value).__name__, value)
                    context.add_error(error)
                    return value
            else:
                error = TypeValidationError(context.field_path, "list", type(value).__name__, value)
                context.add_error(error)
                return value

        # Length constraint validation
        self._validate_length_constraints(value, context)

        # Item validation with error limiting
        validated_items = self._validate_items(value, context)

        return validated_items

    def _validate_length_constraints(self, value: ListType[Any], context: ValidationContext) -> None:
        """Validate list length constraints."""
        value_length = len(value)

        if self.min_length is not None and value_length < self.min_length:
            if self.max_length is not None:
                constraint = f"must contain between {self.min_length} and {self.max_length} items"
            else:
                constraint = f"must contain at least {self.min_length} items"
            context.add_error(ConstraintError(context.field_path, constraint, value))

        if self.max_length is not None and value_length > self.max_length:
            if self.min_length is not None:
                constraint = f"must contain between {self.min_length} and {self.max_length} items"
            else:
                constraint = f"must contain at most {self.max_length} items"
            context.add_error(ConstraintError(context.field_path, constraint, value))

    def _validate_items(self, value: ListType[Any], context: ValidationContext) -> ListType[Any]:
        """Validate individual list items with error limiting."""
        validated_items = []
        item_error_count = 0

        for index, item in enumerate(value):
            # Create child context for item validation
            item_context = context.create_child(f"[{index}]")

            # Validate item
            validated_item = self.item_field.validate(item, item_context)
            validated_items.append(validated_item)

            # Track item errors for limiting
            if item_context.has_errors():
                item_error_count += 1

                # Stop validating items if we've hit the error limit
                if item_error_count >= self.max_item_errors:
                    remaining_items = len(value) - index - 1
                    if remaining_items > 0:
                        summary_context = context.create_child(f"[{index+1}+]")
                        error = ValidationError(
                            f"Validation stopped after {self.max_item_errors} item errors. " f"{remaining_items} items remaining.",
                            summary_context.field_path,
                        )
                        context.add_error(error)
                        # Add remaining items without validation
                        validated_items.extend(value[index + 1 :])
                    break

        return validated_items

    def __repr__(self) -> str:
        constraints = []
        if self.min_length is not None:
            constraints.append(f"min_length={self.min_length}")
        if self.max_length is not None:
            constraints.append(f"max_length={self.max_length}")

        constraint_str = f", {', '.join(constraints)}" if constraints else ""
        return f"ListField({self.item_field}{constraint_str})"
