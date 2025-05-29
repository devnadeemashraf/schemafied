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


class TestIntegration(unittest.TestCase):
    """Integration tests for complete validation scenarios."""

    def test_user_profile_schema(self):
        """Test realistic user profile validation."""
        schema = Schema(
            {
                "user_id": NumberField(min_value=1),
                "profile": DictField(
                    {
                        "name": StringField(min_length=1, max_length=100),
                        "email": StringField(pattern=r"^[^@]+@[^@]+\.[^@]+$"),
                        "age": NumberField(min_value=13, max_value=120, required=False),
                        "bio": StringField(max_length=500, required=False),
                    }
                ),
                "preferences": DictField(
                    {
                        "theme": StringField(required=False, default="light"),
                        "notifications": ListField(StringField(max_length=20), required=False, default=[]),
                        "language": StringField(required=False, default="en"),
                    },
                    required=False,
                ),
                "tags": ListField(
                    StringField(min_length=1, max_length=20),
                    max_length=10,
                    required=False,
                ),
            }
        )

        # Valid data
        valid_data = {
            "user_id": 12345,
            "profile": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "age": 28,
                "bio": "Software developer with a passion for Python",
            },
            "preferences": {
                "theme": "dark",
                "notifications": ["email", "push"],
                "language": "en",
            },
            "tags": ["python", "coding", "tech"],
        }

        result = schema.validate(valid_data)

        # Verify structure is preserved
        self.assertEqual(result["user_id"], 12345)
        self.assertEqual(result["profile"]["name"], "Alice Johnson")
        self.assertEqual(result["profile"]["email"], "alice@example.com")
        self.assertEqual(len(result["tags"]), 3)

    def test_complex_error_aggregation(self):
        """Test that complex nested errors are properly aggregated."""
        schema = Schema(
            {
                "users": ListField(
                    DictField(
                        {
                            "name": StringField(min_length=2, max_length=50),
                            "age": NumberField(min_value=0, max_value=120),
                            "contacts": ListField(
                                DictField(
                                    {
                                        "type": StringField(min_length=1),
                                        "value": StringField(min_length=1),
                                    }
                                ),
                                max_length=5,
                            ),
                        }
                    ),
                    max_length=100,
                ),
                "metadata": DictField(
                    {
                        "version": NumberField(min_value=1),
                        "created_by": StringField(min_length=1),
                    }
                ),
            }
        )

        # Data with multiple nested errors
        invalid_data = {
            "users": [
                {
                    "name": "A",  # Too short
                    "age": 150,  # Too high
                    "contacts": [
                        {"type": "email", "value": ""},  # Empty value
                        {"type": "", "value": "valid"},  # Empty type
                    ],
                },
                {"name": "Valid Name", "age": -5, "contacts": []},  # Negative age
            ],
            "metadata": {
                "version": 0,  # Below minimum
                "created_by": "",  # Empty string
            },
        }

        with self.assertRaises(ValidationErrorCollection) as context:
            schema.validate(invalid_data)

        errors = context.exception.errors
        error_paths = [error.field_path for error in errors]

        # Check that all nested errors are captured with correct paths
        expected_path_patterns = [
            "users[0].name",
            "users[0].age",
            "users[0].contacts[0].value",
            "users[0].contacts[1].type",
            "users[1].age",
            "metadata.version",
            "metadata.created_by",
        ]

        for pattern in expected_path_patterns:
            self.assertTrue(
                any(pattern in path for path in error_paths),
                f"Expected error path pattern '{pattern}' not found in {error_paths}",
            )

    def test_api_response_validation(self):
        """Test validation of API response-like data."""
        api_schema = Schema(
            {
                "status": StringField(pattern=r"^(success|error|pending)$"),
                "data": DictField(
                    {
                        "items": ListField(
                            DictField(
                                {
                                    "id": NumberField(min_value=1),
                                    "title": StringField(min_length=1, max_length=200),
                                    "created_at": StringField(),  # ISO timestamp
                                    "metadata": DictField(
                                        {
                                            "views": NumberField(min_value=0, required=False),
                                            "rating": NumberField(min_value=1, max_value=5, required=False),
                                        },
                                        required=False,
                                    ),
                                }
                            ),
                            max_length=1000,
                        ),
                        "pagination": DictField(
                            {
                                "page": NumberField(min_value=1),
                                "per_page": NumberField(min_value=1, max_value=100),
                                "total": NumberField(min_value=0),
                            }
                        ),
                    }
                ),
                "errors": ListField(StringField(), required=False, default=[]),
            }
        )

        # Valid API response
        api_data = {
            "status": "success",
            "data": {
                "items": [
                    {
                        "id": 1,
                        "title": "First Item",
                        "created_at": "2023-01-01T00:00:00Z",
                        "metadata": {"views": 100, "rating": 4},
                    },
                    {
                        "id": 2,
                        "title": "Second Item",
                        "created_at": "2023-01-02T00:00:00Z",
                    },
                ],
                "pagination": {"page": 1, "per_page": 20, "total": 2},
            },
        }

        result = api_schema.validate(api_data)

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["data"]["items"]), 2)
        self.assertEqual(result["data"]["pagination"]["total"], 2)

    def test_configuration_schema(self):
        """Test validation of application configuration."""
        config_schema = Schema(
            {
                "database": DictField(
                    {
                        "host": StringField(required=False, default="localhost"),  # Make optional
                        "port": NumberField(min_value=1, max_value=65535, required=False, default=5432),
                        "name": StringField(min_length=1),
                        "user": StringField(min_length=1),
                        "password": StringField(min_length=1),
                        "ssl": StringField(
                            pattern=r"^(require|prefer|disable)$",
                            required=False,
                            default="prefer",
                        ),
                    }
                ),
                "cache": DictField(
                    {
                        "backend": StringField(pattern=r"^(redis|memcached|memory)$"),
                        "ttl": NumberField(min_value=0, default=3600),
                        "max_entries": NumberField(min_value=1, default=1000),
                    },
                    required=False,
                ),
                "logging": DictField(
                    {
                        "level": StringField(
                            pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
                            required=False,
                            default="INFO",
                        ),
                        "handlers": ListField(
                            StringField(pattern=r"^(console|file|syslog)$"),
                            min_length=1,
                        ),
                    }
                ),
            }
        )

        # Minimal valid configuration
        config_data = {
            "database": {
                "name": "myapp",
                "user": "dbuser",
                "password": "secret123",
                # host, port, ssl should get defaults
            },
            "logging": {
                "handlers": ["console", "file"]
                # level should get default
            },
        }

        result = config_schema.validate(config_data)

        # Check that required fields are present
        self.assertEqual(result["database"]["name"], "myapp")
        self.assertEqual(result["database"]["user"], "dbuser")
        self.assertEqual(result["database"]["password"], "secret123")

        # Check defaults are applied
        # Add Check for Defaults if they are valid
        self.assertIn("database", result)
        self.assertIn("logging", result)

    def test_error_message_clarity(self):
        """Test that error messages are clear and actionable."""
        schema = Schema(
            {
                "settings": DictField(
                    {
                        "timeout": NumberField(min_value=1, max_value=300),
                        "retries": NumberField(min_value=0, max_value=10),
                    }
                )
            }
        )

        invalid_data = {"settings": {"timeout": 500, "retries": -1}}  # Too high  # Too low

        with self.assertRaises(ValidationErrorCollection) as context:
            schema.validate(invalid_data)

        error_message = str(context.exception)

        # Check that error message includes field paths and constraints
        self.assertIn("settings.timeout", error_message)
        self.assertIn("settings.retries", error_message)
        self.assertIn("must be", error_message.lower())


if __name__ == "__main__":
    unittest.main()
