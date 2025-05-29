import unittest


from schemafied import (
    # Base
    Schema,
    # Fields
    NumberField,
    ListField,
    DictField,
    StringField,
    # Exceptions
    ValidationError,
    ValidationErrorCollection,
    MissingFieldError,
)


class TestSchema(unittest.TestCase):
    """Test cases for the Schema class."""

    def setUp(self):
        """Set up test schemas."""
        self.simple_schema = Schema(
            {
                "name": StringField(min_length=1, max_length=50),
                "age": NumberField(min_value=0, max_value=120),
            }
        )

        self.nested_schema = Schema(
            {
                "user": DictField(
                    {
                        "profile": DictField(
                            {
                                "name": StringField(required=True),
                                "age": NumberField(min_value=0, max_value=120),
                            }
                        ),
                        "preferences": DictField(
                            {
                                "theme": StringField(required=False, default="light"),
                                "notifications": ListField(StringField(), required=False),
                            },
                            required=False,
                        ),
                    }
                )
            }
        )

    def test_valid_simple_schema(self):
        """Test validation with valid simple data."""
        data = {"name": "Alice", "age": 30}
        result = self.simple_schema.validate(data)

        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["age"], 30)

    def test_missing_required_field(self):
        """Test validation fails for missing required fields."""
        data = {"name": "Alice"}  # Missing required 'age'

        with self.assertRaises(MissingFieldError) as context:
            self.simple_schema.validate(data)

        error = context.exception
        self.assertEqual(error.field_path, "age")
        self.assertIn("required", error.message)

    def test_multiple_validation_errors(self):
        """Test that multiple errors are collected and reported."""
        data = {"name": "", "age": 150}  # Too short  # Too high

        with self.assertRaises(ValidationErrorCollection) as context:
            self.simple_schema.validate(data)

        errors = context.exception.errors
        self.assertEqual(len(errors), 2)

        # Check that both field errors are present
        field_paths = [error.field_path for error in errors]
        self.assertIn("name", field_paths)
        self.assertIn("age", field_paths)

    def test_nested_schema_validation(self):
        """Test validation of nested dictionary structures."""
        data = {
            "user": {
                "profile": {"name": "Bob", "age": 25},
                "preferences": {"theme": "dark", "notifications": ["email", "sms"]},
            }
        }

        result = self.nested_schema.validate(data)
        self.assertEqual(result["user"]["profile"]["name"], "Bob")
        self.assertEqual(result["user"]["profile"]["age"], 25)
        self.assertEqual(result["user"]["preferences"]["theme"], "dark")
        self.assertEqual(len(result["user"]["preferences"]["notifications"]), 2)

    def test_nested_validation_errors_with_paths(self):
        """Test that nested validation errors have correct field paths."""
        data = {
            "user": {
                "profile": {
                    "name": "",  # Invalid: too short
                    "age": -5,  # Invalid: below minimum
                }
            }
        }

        # Expect ValidationErrorCollection for multiple errors
        with self.assertRaises((ValidationError, ValidationErrorCollection)) as context:
            self.nested_schema.validate(data)

        # Handle both single error and collection cases
        if isinstance(context.exception, ValidationErrorCollection):
            errors = context.exception.errors
        else:
            errors = [context.exception]

        error_paths = [error.field_path for error in errors]

        # Check that we have nested paths
        has_nested_paths = any("user.profile" in path for path in error_paths)
        self.assertTrue(has_nested_paths, f"Expected nested paths in: {error_paths}")

    def test_type_coercion(self):
        """Test automatic type coercion where appropriate."""
        data = {"name": "Alice", "age": "30"}  # Age as string

        result = self.simple_schema.validate(data)
        self.assertEqual(result["age"], 30)
        self.assertIsInstance(result["age"], int)

    def test_strict_mode_extra_fields(self):
        """Test strict mode rejects extra fields."""
        strict_schema = Schema({"name": StringField()}, strict=True)

        data = {"name": "Alice", "extra": "field"}

        # Expect a single ValidationError (not collection) for strict mode
        with self.assertRaises(ValidationError) as context:
            strict_schema.validate(data)

        error = context.exception
        self.assertIn("extra", str(error).lower())

    def test_non_strict_mode_ignores_extra_fields(self):
        """Test non-strict mode ignores extra fields."""
        data = {"name": "Alice", "age": 30, "extra": "field"}

        result = self.simple_schema.validate(data)

        # Should only contain schema fields
        self.assertEqual(set(result.keys()), {"name", "age"})
        self.assertNotIn("extra", result)

    def test_invalid_root_type(self):
        """Test validation fails for non-dictionary root data."""
        with self.assertRaises(ValidationError) as context:
            self.simple_schema.validate("not a dictionary")

        error = context.exception
        self.assertIn("Expected dictionary", error.message)

    def test_partial_validation(self):
        """Test partial validation method."""
        data = {"name": "Alice", "age": 150}  # Age is invalid

        result = self.simple_schema.validate_partial(data)

        self.assertFalse(result["is_valid"])
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIsInstance(result["data"], dict)

    def test_default_values(self):
        """Test handling of default values for optional fields."""
        schema_with_defaults = Schema(
            {
                "name": StringField(),
                "status": StringField(required=False, default="active"),
                "score": NumberField(required=False, default=0),
            }
        )

        data = {"name": "Alice"}
        result = schema_with_defaults.validate(data)

        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["score"], 0)


if __name__ == "__main__":
    unittest.main()
