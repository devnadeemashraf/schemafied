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
    ValidationErrorCollection,
)


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and unusual scenarios."""

    def test_empty_data_structures(self):
        """Test validation of empty data structures."""
        schema = Schema(
            {
                "empty_string": StringField(min_length=0, required=False),
                "empty_list": ListField(StringField(), min_length=0, required=False),
                "empty_dict": DictField({}, required=False),
            }
        )

        data = {"empty_string": "", "empty_list": [], "empty_dict": {}}

        result = schema.validate(data)

        self.assertEqual(result["empty_string"], "")
        self.assertEqual(result["empty_list"], [])
        self.assertEqual(result["empty_dict"], {})

    def test_null_and_none_handling(self):
        """Test handling of null/None values."""
        schema = Schema(
            {
                "required_field": StringField(required=True),
                "optional_field": StringField(required=False, default="default"),
                "nullable_field": StringField(required=False),
            }
        )

        # Test with None values
        data = {
            "required_field": "present",
            "optional_field": None,
            "nullable_field": None,
        }

        result = schema.validate(data)

        self.assertEqual(result["required_field"], "present")
        self.assertEqual(result["optional_field"], "default")
        self.assertEqual(result["nullable_field"], None)

    def test_circular_reference_handling(self):
        """Test handling of circular references in input data."""
        schema = Schema({"name": StringField(), "metadata": DictField({"info": StringField()})})

        # Create data with circular reference
        data = {"name": "test"}
        data["metadata"] = {"info": "test", "circular": data}

        # Should validate successfully, ignoring extra 'circular' field
        result = schema.validate(data)

        self.assertEqual(result["name"], "test")
        self.assertEqual(result["metadata"]["info"], "test")
        self.assertNotIn("circular", result["metadata"])

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        schema = Schema(
            {
                "unicode_text": StringField(max_length=100),
                "emoji_text": StringField(max_length=50),
                "special_chars": StringField(),
            }
        )

        data = {
            "unicode_text": "Hello 世界 🌍",
            "emoji_text": "😀😁😂🤣😃😄😅😆😉",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
        }

        result = schema.validate(data)

        self.assertEqual(result["unicode_text"], "Hello 世界 🌍")
        self.assertEqual(result["emoji_text"], "😀😁😂🤣😃😄😅😆😉")
        self.assertEqual(result["special_chars"], "!@#$%^&*()_+-=[]{}|;':\",./<>?")

    def test_numeric_edge_cases(self):
        """Test numeric edge cases like infinity, NaN, etc."""
        schema = Schema(
            {
                "large_number": NumberField(),
                "small_number": NumberField(),
                "zero": NumberField(min_value=0, max_value=0),
            }
        )

        data = {
            "large_number": 1.7976931348623157e308,  # Near max float
            "small_number": 2.2250738585072014e-308,  # Near min positive float
            "zero": 0,
        }

        result = schema.validate(data)

        self.assertEqual(result["large_number"], 1.7976931348623157e308)
        self.assertEqual(result["small_number"], 2.2250738585072014e-308)
        self.assertEqual(result["zero"], 0)

    def test_string_coercion_edge_cases(self):
        """Test string coercion with unusual values."""
        schema = Schema(
            {
                "from_bool": StringField(coerce=True),
                "from_none": StringField(coerce=True, required=False),
                "from_list": StringField(coerce=True),
                "from_dict": StringField(coerce=True),
            }
        )

        data = {
            "from_bool": True,
            "from_none": None,
            "from_list": [1, 2, 3],
            "from_dict": {"key": "value"},
        }

        result = schema.validate(data)

        self.assertEqual(result["from_bool"], "True")
        self.assertEqual(result["from_none"], None)
        self.assertEqual(result["from_list"], "[1, 2, 3]")
        self.assertIn("key", result["from_dict"])

    def test_nested_list_of_dicts(self):
        """Test deeply nested list of dictionaries."""
        schema = Schema(
            {
                "data": ListField(
                    DictField(
                        {
                            "id": NumberField(min_value=1),
                            "items": ListField(
                                DictField(
                                    {
                                        "name": StringField(min_length=1),
                                        "value": NumberField(),
                                    }
                                )
                            ),
                        }
                    )
                )
            }
        )

        data = {
            "data": [
                {
                    "id": 1,
                    "items": [
                        {"name": "item1", "value": 10},
                        {"name": "item2", "value": 20},
                    ],
                },
                {"id": 2, "items": [{"name": "item3", "value": 30}]},
            ]
        }

        result = schema.validate(data)

        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(len(result["data"][0]["items"]), 2)
        self.assertEqual(result["data"][0]["items"][0]["name"], "item1")

    def test_extremely_large_valid_datasets(self):
        """Test with large but valid datasets."""
        schema = Schema(
            {
                "bulk_data": ListField(
                    DictField(
                        {
                            "id": NumberField(min_value=1),
                            "name": StringField(max_length=100),
                        }
                    ),
                    max_length=10000,
                )
            }
        )

        # Create large valid dataset
        large_data = {"bulk_data": [{"id": i, "name": f"Item {i}"} for i in range(1, 1001)]}  # 1000 items

        result = schema.validate(large_data)

        self.assertEqual(len(result["bulk_data"]), 1000)
        self.assertEqual(result["bulk_data"][0]["id"], 1)
        self.assertEqual(result["bulk_data"][999]["name"], "Item 1000")

    def test_malformed_input_types(self):
        """Test handling of completely wrong input types."""
        schema = Schema(
            {
                "expected_dict": DictField({"key": StringField()}),
                "expected_list": ListField(NumberField()),
                "expected_string": StringField(),
                "expected_number": NumberField(),
            }
        )

        # Completely wrong types
        malformed_data = {
            "expected_dict": "not a dict",
            "expected_list": 42,
            "expected_string": {"not": "string"},
            "expected_number": ["not", "number"],
        }

        with self.assertRaises(ValidationErrorCollection) as context:
            schema.validate(malformed_data)

        errors = context.exception.errors

        # Should have type errors for all fields
        self.assertEqual(len(errors), 3)

        # Check error types and messages
        for error in errors:
            self.assertIn("Expected", error.message)


if __name__ == "__main__":
    unittest.main()
