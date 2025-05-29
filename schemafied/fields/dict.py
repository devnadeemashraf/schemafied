from typing import Any, Dict as DictType


from .base import Field
from ..validation_context import ValidationContext
from ..exceptions import ValidationError, TypeValidationError


class DictField(Field):
    """
    Field for validating nested dictionaries against a schema.

    Validates that the value is a dictionary and that all fields conform
    to their respective field definitions in the schema.
    """

    def __init__(self, schema: DictType[str, Field], strict: bool = False, **kwargs):
        """
        Initialize DictField with a nested schema.

        Args:
            schema: Dictionary mapping field names to Field instances
            strict: If True, reject dictionaries with extra fields
            **kwargs: Additional field parameters
        """
        super().__init__(**kwargs)
        self.schema = schema
        self.strict = strict

    def _validate_type(self, value: Any, context: ValidationContext) -> DictType[str, Any]:
        """Validate dictionary type and structure."""
        # Type validation with coercion
        if not isinstance(value, dict):
            if self.coerce and hasattr(value, "items"):
                try:
                    value = dict(value)
                except (TypeError, ValueError):
                    error = TypeValidationError(context.field_path, "dictionary", type(value).__name__, value)
                    context.add_error(error)
                    return value
            else:
                error = TypeValidationError(context.field_path, "dictionary", type(value).__name__, value)
                context.add_error(error)
                return value

        # Validate against schema
        validated_data = self._validate_schema(value, context)

        # Check for extra fields if in strict mode
        if self.strict:
            self._check_extra_fields(value, context)

        return validated_data

    def _validate_schema(self, value: DictType[str, Any], context: ValidationContext) -> DictType[str, Any]:
        """Validate dictionary against the schema."""
        validated_data = {}

        for field_name, field in self.schema.items():
            # Create child context for field validation
            field_context = context.create_child(field_name)

            # Get field value
            field_value = value.get(field_name)

            # Validate field
            validated_value = field.validate(field_value, field_context)

            # Only include in result if validation succeeded
            if not field_context.has_errors():
                validated_data[field_name] = validated_value

        return validated_data

    def _check_extra_fields(self, value: DictType[str, Any], context: ValidationContext) -> None:
        """Check for extra fields in strict mode."""
        extra_fields = set(value.keys()) - set(self.schema.keys())

        for extra_field in extra_fields:
            extra_context = context.create_child(extra_field)
            error = ValidationError("Extra field not allowed in strict mode", extra_context.field_path)
            context.add_error(error)

    def __repr__(self):
        field_names = list(self.schema.keys())
        if len(field_names) <= 3:
            fields_str = f"[{', '.join(field_names)}]"
        else:
            fields_str = f"[{', '.join(field_names[:3])}, ...]"

        strict_str = ", strict=True" if self.strict else ""
        return f"DictField({fields_str}{strict_str})"
