from typing import Dict, Any, List


from .fields.base import Field
from .validation_context import ValidationContext
from .exceptions import ValidationError, ValidationErrorCollection, TypeValidationError


class Schema:
    """
    Root schema class for validating dictionaries against defined field schemas.

    The Schema class serves as the main entry point for validation operations,
    orchestrating field validation and error aggregation.
    """

    def __init__(self, fields: Dict[str, Field], strict: bool = False, description: str = "") -> None:
        """
        Initialize schema with field definitions.

        Args:
            fields: Dictionary mapping field names to Field instances
            strict: If True, reject data with extra fields not in schema
            description: Human-readable description of the schema
        """
        self.fields = fields
        self.strict = strict
        self.description = description

    def validate(self, data: Any) -> Dict[str, Any]:
        """
        Validate data against this schema.

        Args:
            data: Data to validate (expected to be a dictionary)

        Returns:
            Validated data dictionary with coerced values

        Raises:
            ValidationError: For single validation errors
            ValidationErrorCollection: For multiple validation errors
        """
        # Create root validation context
        context = ValidationContext()

        # Type validation for root data
        if not isinstance(data, dict):
            error = TypeValidationError("", "dictionary", type(data).__name__, data)
            raise ValidationError(error.message)

        # Validate each field in the schema
        validated_data = self._validate_fields(data, context)

        # Check for extra fields if in strict mode
        if self.strict:
            self._check_extra_fields(data, context)

        # Raise errors if any were collected
        all_errors = context.collect_all_errors()
        if all_errors:
            if len(all_errors) == 1:
                raise all_errors[0]
            else:
                raise ValidationErrorCollection(all_errors)

        return validated_data

    def _validate_fields(self, data: Dict[str, Any], context: ValidationContext) -> Dict[str, Any]:
        """Validate all fields in the schema."""
        validated_data = {}

        for field_name, field in self.fields.items():
            # Create child context for this field
            field_context = context.create_child(field_name)

            # Get field value from data
            field_value = data.get(field_name)

            # Validate the field
            validated_value = field.validate(field_value, field_context)

            # Only include in result if no errors occurred for this field
            if not field_context.has_errors():
                validated_data[field_name] = validated_value

        return validated_data

    def _check_extra_fields(self, data: Dict[str, Any], context: ValidationContext) -> None:
        """Check for extra fields when in strict mode."""
        extra_fields = set(data.keys()) - set(self.fields.keys())

        for extra_field in extra_fields:
            error = ValidationError("Extra field not allowed in strict mode", extra_field)
            context.add_error(error)

    def validate_partial(self, data: Any) -> Dict[str, Any]:
        """
        Validate data but return partial results even if there are errors.

        This method performs validation but returns a dictionary containing
        both successfully validated data and error information.

        Args:
            data: Data to validate

        Returns:
            Dictionary with 'data', 'errors', and 'is_valid' keys
        """
        try:
            validated_data = self.validate(data)
            return {"data": validated_data, "errors": [], "is_valid": True}
        except ValidationError as e:
            return {"data": {}, "errors": [e], "is_valid": False}
        except ValidationErrorCollection as e:
            return {"data": {}, "errors": e.errors, "is_valid": False}

    def get_field_names(self) -> List[str]:
        """Get list of field names in this schema."""
        return list(self.fields.keys())

    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [name for name, field in self.fields.items() if field.required]

    def get_optional_fields(self) -> List[str]:
        """Get list of optional field names."""
        return [name for name, field in self.fields.items() if not field.required]

    def __repr__(self) -> str:
        field_count = len(self.fields)
        strict_str = ", strict=True" if self.strict else ""
        return f"Schema({field_count} fields{strict_str})"
