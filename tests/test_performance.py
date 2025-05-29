import unittest
import time


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


class TestPerformance(unittest.TestCase):
    """Performance tests for validation operations."""

    def test_large_list_validation_performance(self):
        """Test validation performance with large lists."""
        schema = Schema(
            {
                "items": ListField(
                    NumberField(min_value=0, max_value=1000),
                    max_item_errors=10,  # Limit errors for performance
                )
            }
        )

        # Test with valid large list
        large_valid_list = list(range(1000))
        data = {"items": large_valid_list}

        start_time = time.time()
        result = schema.validate(data)
        end_time = time.time()

        elapsed = end_time - start_time
        self.assertLess(elapsed, 1.0, "Large list validation took too long")
        self.assertEqual(len(result["items"]), 1000)

    def test_large_list_with_errors_performance(self):
        """Test performance when many list items have errors."""
        schema = Schema(
            {
                "items": ListField(
                    NumberField(min_value=0, max_value=100),
                    max_item_errors=5,  # Strict error limiting
                )
            }
        )

        # Create list where most items are invalid
        invalid_list = list(range(200, 1200))  # 1000 items, all exceed max_value
        data = {"items": invalid_list}

        start_time = time.time()
        with self.assertRaises(ValidationErrorCollection):
            schema.validate(data)
        end_time = time.time()

        elapsed = end_time - start_time
        self.assertLess(elapsed, 2.0, "Error-heavy validation took too long")

    def test_deep_nesting_performance(self):
        """Test performance with deeply nested structures."""
        # Create a deeply nested schema
        nested_schema = Schema(
            {
                "level1": DictField(
                    {
                        "level2": DictField(
                            {
                                "level3": DictField(
                                    {
                                        "level4": DictField(
                                            {
                                                "level5": DictField(
                                                    {
                                                        "data": ListField(
                                                            NumberField(
                                                                min_value=0,
                                                                max_value=100,
                                                            ),
                                                            max_length=50,
                                                        )
                                                    }
                                                )
                                            }
                                        )
                                    }
                                )
                            }
                        )
                    }
                )
            }
        )

        # Create deeply nested data
        nested_data = {"level1": {"level2": {"level3": {"level4": {"level5": {"data": list(range(50))}}}}}}

        start_time = time.time()
        result = nested_schema.validate(nested_data)
        end_time = time.time()

        elapsed = end_time - start_time
        self.assertLess(elapsed, 1.0, "Deep nesting validation took too long")

        # Verify structure is preserved
        self.assertEqual(len(result["level1"]["level2"]["level3"]["level4"]["level5"]["data"]), 50)

    def test_schema_reuse_performance(self):
        """Test performance when reusing schemas multiple times."""
        schema = Schema(
            {
                "name": StringField(min_length=1, max_length=100),
                "age": NumberField(min_value=0, max_value=120),
                "tags": ListField(StringField(max_length=20), max_length=10),
            }
        )

        # Validate multiple different datasets with same schema
        datasets = [
            {
                "name": f"User {i}",
                "age": 20 + (i % 50),
                "tags": [f"tag{j}" for j in range(i % 5)],
            }
            for i in range(100)
        ]

        start_time = time.time()
        results = []
        for data in datasets:
            result = schema.validate(data)
            results.append(result)
        end_time = time.time()

        elapsed = end_time - start_time
        avg_time = elapsed / len(datasets)

        self.assertEqual(len(results), 100)
        self.assertLess(avg_time, 0.01, f"Average validation time too high: {avg_time}")

    def test_memory_usage_with_large_errors(self):
        """Test memory usage when collecting many validation errors."""
        schema = Schema(
            {
                "numbers": ListField(
                    NumberField(min_value=1000, max_value=2000),
                    max_item_errors=50,  # Allow more errors for this test
                )
            }
        )

        # Create data that will generate many errors
        invalid_data = {"numbers": list(range(100))}  # All items below minimum

        try:
            schema.validate(invalid_data)
        except ValidationErrorCollection as e:
            # Check that error collection is reasonably sized
            self.assertLessEqual(len(e.errors), 60)  # Should be limited

            # Check memory usage of error messages isn't excessive
            total_message_length = sum(len(error.message) for error in e.errors)
            self.assertLess(total_message_length, 10000, "Error messages too verbose")


if __name__ == "__main__":
    unittest.main()
