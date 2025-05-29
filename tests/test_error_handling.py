import unittest


from schemafied import (
    # Base
    Schema,
    ValidationContext,
    # Fields
    NumberField,
    ListField,
    StringField,
    # Exceptions
    ValidationError,
    ValidationErrorCollection,
    MissingFieldError,
    ConstraintError,
    TypeValidationError,
)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and reporting."""

    def test_validation_context_hierarchy(self):
        """Test that ValidationContext properly tracks field hierarchy."""
        root_context = ValidationContext()

        # Create nested contexts
        user_context = root_context.create_child("user")
        profile_context = user_context.create_child("profile")
        name_context = profile_context.create_child("name")

        # Add error to deeply nested context
        error = ValidationError("Test error")
        name_context.add_error(error)

        # Check field path is built correctly
        self.assertEqual(error.field_path, "user.profile.name")

        # Check error propagation
        all_errors = root_context.collect_all_errors()
        self.assertEqual(len(all_errors), 1)
        self.assertEqual(all_errors[0].field_path, "user.profile.name")

    def test_array_index_field_paths(self):
        """Test field paths for array indices."""
        context = ValidationContext("users")

        # Create array index context
        item_context = context.create_child("[0]")
        field_context = item_context.create_child("name")

        error = ValidationError("Test error")
        field_context.add_error(error)

        self.assertEqual(error.field_path, "users[0].name")

    def test_error_collection_grouping(self):
        """Test error collection groups errors by field."""
        schema = Schema(
            {
                "field1": NumberField(min_value=10, max_value=20),
                "field2": StringField(min_length=5, max_length=10),
                "field3": ListField(NumberField(min_value=0, max_value=100)),
            }
        )

        invalid_data = {
            "field1": 5,  # Below minimum
            "field2": "ab",  # Too short
            "field3": [150, 200],  # Items exceed maximum
        }

        with self.assertRaises(ValidationErrorCollection) as context:
            schema.validate(invalid_data)

        errors_by_field = context.exception.get_errors_by_field()

        # Check each field has errors
        self.assertIn("field1", errors_by_field)
        self.assertIn("field2", errors_by_field)

        # Check array item errors
        array_error_fields = [field for field in errors_by_field.keys() if "field3[" in field]
        self.assertTrue(len(array_error_fields) > 0)

    def test_custom_validator_error_handling(self):
        """Test error handling for custom validators."""

        def must_be_even(value):
            if value % 2 != 0:
                return "Value must be even"
            return True

        def must_be_positive(value):
            if value <= 0:
                raise ValueError("Value must be positive")
            return True

        schema = Schema(
            {
                "even_number": NumberField(validators=[must_be_even]),
                "positive_number": NumberField(validators=[must_be_positive]),
            }
        )

        invalid_data = {
            "even_number": 3,  # Odd number
            "positive_number": -5,  # Negative number
        }

        with self.assertRaises(ValidationErrorCollection) as context:
            schema.validate(invalid_data)

        errors = context.exception.errors
        error_messages = [error.message for error in errors]

        # Check custom error messages
        self.assertTrue(any("must be even" in msg.lower() for msg in error_messages))
        self.assertTrue(any("must be positive" in msg.lower() for msg in error_messages))

    def test_error_limiting_in_large_lists(self):
        """Test that error reporting is limited for large lists."""
        schema = Schema({"numbers": ListField(NumberField(min_value=0, max_value=10), max_item_errors=3)})

        # Create list with many invalid items
        invalid_data = {"numbers": list(range(50, 70))}  # All items exceed max_value=10

        with self.assertRaises(ValidationErrorCollection) as context:
            schema.validate(invalid_data)

        errors = context.exception.errors

        # Should have limited number of errors plus summary
        self.assertLessEqual(len(errors), 5)

        # Check for error limiting message
        error_messages = [error.message for error in errors]
        summary_message = any("stopped after" in msg.lower() for msg in error_messages)
        self.assertTrue(summary_message)

    def test_missing_field_error_details(self):
        """Test detailed information in missing field errors."""
        schema = Schema(
            {
                "required_field": StringField(required=True),
                "optional_field": StringField(required=False),
            }
        )

        with self.assertRaises(MissingFieldError) as context:
            schema.validate({})

        error = context.exception
        self.assertEqual(error.field_path, "required_field")
        self.assertEqual(error.error_code, "required")
        self.assertIn("required", error.message)

    def test_constraint_error_details(self):
        """Test detailed information in constraint errors."""
        schema = Schema({"age": NumberField(min_value=18, max_value=65)})

        with self.assertRaises(ConstraintError) as context:
            schema.validate({"age": 10})

        error = context.exception
        self.assertEqual(error.field_path, "age")
        self.assertEqual(error.error_code, "constraint")
        self.assertIn("between 18 and 65", error.message)
        self.assertEqual(error.value, 10)

    def test_type_validation_error_details(self):
        """Test detailed information in type validation errors."""
        schema = Schema({"count": NumberField(coerce=False)})

        with self.assertRaises(TypeValidationError) as context:
            schema.validate({"count": "not a number"})

        error = context.exception
        self.assertEqual(error.field_path, "count")
        self.assertEqual(error.error_code, "type_error")
        self.assertEqual(error.expected_type, "number")
        self.assertIn("str", error.actual_type)

    def test_validation_error_string_representation(self):
        """Test string representation of validation errors."""
        error = ValidationError("Test message", "test.field", "test_code")

        str_repr = str(error)
        self.assertIn("test.field", str_repr)
        self.assertIn("Test message", str_repr)

    def test_validation_error_collection_formatting(self):
        """Test formatting of ValidationErrorCollection."""
        errors = [
            ValidationError("First error", "field1"),
            ValidationError("Second error", "field2"),
            ValidationError("Third error", "nested.field"),
        ]

        collection = ValidationErrorCollection(errors)
        formatted = str(collection)

        # Check all errors are included
        self.assertIn("field1", formatted)
        self.assertIn("field2", formatted)
        self.assertIn("nested.field", formatted)
        self.assertIn("First error", formatted)
        self.assertIn("Second error", formatted)
        self.assertIn("Third error", formatted)

    def test_partial_validation_error_handling(self):
        """Test partial validation with mixed valid/invalid data."""
        schema = Schema(
            {
                "valid_field": StringField(max_length=50),
                "invalid_field": NumberField(min_value=100, max_value=200),
            }
        )

        data = {"valid_field": "This is valid", "invalid_field": 50}  # Below minimum

        result = schema.validate_partial(data)

        self.assertFalse(result["is_valid"])
        self.assertTrue(len(result["errors"]) > 0)
        self.assertIsInstance(result["data"], dict)

        # Check error details
        error = result["errors"][0]
        self.assertIn("invalid_field", error.field_path)


if __name__ == "__main__":
    unittest.main()
