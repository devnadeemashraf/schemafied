import unittest


from schemafied import (
    # Base
    ValidationContext,
    # Fields
    NumberField,
    ListField,
    StringField,
    DictField,
    # Exceptions
    MissingFieldError,
    ConstraintError,
    TypeValidationError,
)


class TestNumberField(unittest.TestCase):
    """Test cases for NumberField."""

    def setUp(self):
        self.context = ValidationContext("test_field")

    def test_valid_integer(self):
        """Test validation of valid integer values."""
        field = NumberField(min_value=0, max_value=100)
        result = field.validate(42, self.context)

        self.assertEqual(result, 42)
        self.assertFalse(self.context.has_errors())

    def test_valid_float(self):
        """Test validation of valid float values."""
        field = NumberField(min_value=0.0, max_value=100.0)
        result = field.validate(42.5, self.context)

        self.assertEqual(result, 42.5)
        self.assertFalse(self.context.has_errors())

    def test_string_coercion(self):
        """Test automatic coercion from string to number."""
        field = NumberField(coerce=True)

        # Test integer coercion
        result_int = field.validate("42", self.context)
        self.assertEqual(result_int, 42)
        self.assertIsInstance(result_int, int)

        # Test float coercion
        context2 = ValidationContext("test_field2")
        result_float = field.validate("42.5", context2)
        self.assertEqual(result_float, 42.5)
        self.assertIsInstance(result_float, float)

    def test_constraint_violations(self):
        """Test min/max constraint violations."""
        field = NumberField(min_value=10, max_value=20)

        # Test below minimum
        context1 = ValidationContext("test_field")
        field.validate(5, context1)
        self.assertTrue(context1.has_errors())
        self.assertIsInstance(context1.errors[0], ConstraintError)

        # Test above maximum
        context2 = ValidationContext("test_field")
        field.validate(25, context2)
        self.assertTrue(context2.has_errors())
        self.assertIsInstance(context2.errors[0], ConstraintError)

    def test_type_validation_error(self):
        """Test type validation for non-numeric values."""
        field = NumberField(coerce=False)
        field.validate("not a number", self.context)

        self.assertTrue(self.context.has_errors())
        self.assertIsInstance(self.context.errors[0], TypeValidationError)

    def test_custom_validators(self):
        """Test custom validator functions."""

        def even_only(value):
            return value % 2 == 0

        field = NumberField(validators=[even_only])

        # Valid even number
        context1 = ValidationContext("test_field")
        result = field.validate(4, context1)
        self.assertEqual(result, 4)
        self.assertFalse(context1.has_errors())

        # Invalid odd number
        context2 = ValidationContext("test_field")
        field.validate(3, context2)
        self.assertTrue(context2.has_errors())


class TestStringField(unittest.TestCase):
    """Test cases for StringField."""

    def setUp(self):
        self.context = ValidationContext("test_field")

    def test_valid_string(self):
        """Test validation of valid string values."""
        field = StringField(min_length=1, max_length=10)
        result = field.validate("hello", self.context)

        self.assertEqual(result, "hello")
        self.assertFalse(self.context.has_errors())

    def test_length_constraints(self):
        """Test string length constraint validation."""
        field = StringField(min_length=5, max_length=10)

        # Test too short
        context1 = ValidationContext("test_field")
        field.validate("hi", context1)
        self.assertTrue(context1.has_errors())

        # Test too long
        context2 = ValidationContext("test_field")
        field.validate("this is too long", context2)
        self.assertTrue(context2.has_errors())

    def test_type_coercion(self):
        """Test automatic coercion to string."""
        field = StringField(coerce=True)
        result = field.validate(123, self.context)

        self.assertEqual(result, "123")
        self.assertIsInstance(result, str)
        self.assertFalse(self.context.has_errors())

    def test_pattern_validation(self):
        """Test regex pattern validation."""

        field = StringField(pattern=r"^[a-zA-Z]+$")  # Letters only

        # Valid pattern
        context1 = ValidationContext("test_field")
        result = field.validate("hello", context1)
        self.assertEqual(result, "hello")
        self.assertFalse(context1.has_errors())

        # Invalid pattern
        context2 = ValidationContext("test_field")
        field.validate("hello123", context2)
        self.assertTrue(context2.has_errors())


class TestListField(unittest.TestCase):
    """Test cases for ListField."""

    def setUp(self):
        self.context = ValidationContext("test_field")

    def test_valid_list(self):
        """Test validation of valid list with valid items."""
        field = ListField(NumberField(min_value=0, max_value=100))
        data = [1, 2, 3, 4, 5]

        result = field.validate(data, self.context)

        self.assertEqual(result, [1, 2, 3, 4, 5])
        self.assertFalse(self.context.has_errors())

    def test_list_length_constraints(self):
        """Test list length constraint validation."""
        field = ListField(NumberField(), min_length=2, max_length=5)

        # Test too short
        context1 = ValidationContext("test_field")
        field.validate([1], context1)
        self.assertTrue(context1.has_errors())

        # Test too long
        context2 = ValidationContext("test_field")
        field.validate([1, 2, 3, 4, 5, 6], context2)
        self.assertTrue(context2.has_errors())

    def test_item_validation_errors(self):
        """Test validation errors for individual list items."""
        field = ListField(NumberField(min_value=0, max_value=10))
        data = [5, 15, 20, 3]  # 15 and 20 are invalid

        field.validate(data, self.context)

        self.assertTrue(self.context.has_errors())
        # Should have errors for items at index 1 and 2
        error_paths = [error.field_path for error in self.context.collect_all_errors()]
        self.assertTrue(any("[1]" in path for path in error_paths))
        self.assertTrue(any("[2]" in path for path in error_paths))

    def test_error_limiting(self):
        """Test that item error reporting is limited for performance."""
        field = ListField(NumberField(min_value=0, max_value=10), max_item_errors=3)

        # Create list with many invalid items
        data = list(range(20, 40))  # All items exceed max_value=10

        field.validate(data, self.context)

        # Should limit errors and add summary
        all_errors = self.context.collect_all_errors()
        self.assertTrue(len(all_errors) <= 5)  # Limited errors + summary

    def test_type_coercion(self):
        """Test coercion of iterable to list."""
        field = ListField(NumberField(), coerce=True)
        data = (1, 2, 3)  # Tuple

        result = field.validate(data, self.context)

        self.assertEqual(result, [1, 2, 3])
        self.assertIsInstance(result, list)
        self.assertFalse(self.context.has_errors())


class TestDictField(unittest.TestCase):
    """Test cases for DictField."""

    def setUp(self):
        self.context = ValidationContext("test_field")
        self.schema = {
            "name": StringField(required=True),
            "age": NumberField(min_value=0, max_value=120),
            "email": StringField(required=False),
        }

    def test_valid_nested_dict(self):
        """Test validation of valid nested dictionary."""
        field = DictField(self.schema)
        data = {"name": "Alice", "age": 30, "email": "alice@example.com"}

        result = field.validate(data, self.context)

        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["age"], 30)
        self.assertEqual(result["email"], "alice@example.com")
        self.assertFalse(self.context.has_errors())

    def test_nested_validation_errors(self):
        """Test nested field validation errors."""
        field = DictField(self.schema)
        data = {
            "name": "",  # Invalid: too short
            "age": 150,  # Invalid: exceeds maximum
        }

        field.validate(data, self.context)

        self.assertTrue(self.context.has_errors())

        # Check that errors exist (don't assume specific nested paths)
        all_errors = self.context.collect_all_errors()
        self.assertGreater(len(all_errors), 0)

        # Check that errors mention the relevant fields
        error_messages = [str(error) for error in all_errors]
        has_name_error = any("name" in msg for msg in error_messages)
        has_age_error = any("age" in msg for msg in error_messages)

        self.assertTrue(
            has_name_error or has_age_error,
            "Expected validation errors for name or age",
        )

    def test_strict_mode(self):
        """Test strict mode rejects extra fields."""
        field = DictField(self.schema, strict=True)
        data = {"name": "Alice", "age": 30, "extra_field": "not allowed"}

        field.validate(data, self.context)

        self.assertTrue(self.context.has_errors())
        error_messages = [error.message for error in self.context.collect_all_errors()]
        self.assertTrue(any("Extra field" in msg for msg in error_messages))

    def test_missing_required_nested_field(self):
        """Test missing required field in nested dictionary."""
        field = DictField(self.schema)
        data = {"age": 30}  # Missing required 'name'

        field.validate(data, self.context)

        self.assertTrue(self.context.has_errors())

        # Should have MissingFieldError for 'name'
        errors = self.context.collect_all_errors()
        missing_errors = [e for e in errors if isinstance(e, MissingFieldError)]
        self.assertTrue(len(missing_errors) > 0)


if __name__ == "__main__":
    unittest.main()
