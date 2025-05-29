# Schemafied

A Python library for validating data structures against user-defined schemas with comprehensive error reporting and nested structure support.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/schemafied.svg)](https://pypi.org/project/schemafied/)

## Features

- 🔍 **Declarative Schema Definition** - Define validation rules using intuitive field classes
- 🎯 **Comprehensive Error Aggregation** - Collect all validation errors, not just the first one
- 🏗️ **Nested Structure Support** - Validate complex nested dictionaries and lists
- 🔧 **Type Coercion** - Automatically convert compatible types (strings to numbers, etc.)
- 📍 **Precise Error Paths** - Get exact field paths for errors (e.g., `users[0].profile.age`)
- ⚡ **Performance Optimized** - Error limiting for large datasets
- 🎨 **Extensible** - Custom validators and field types
- 🛡️ **Type Safe** - Full type hint support

## Quick Start

### Installation

```bash
pip install schemafied
```

### Basic Usage

```python
from schemafied import Schema, NumberField, StringField

# Define your schema
schema = Schema({
    "name": StringField(min_length=1, max_length=100),
    "age": NumberField(min_value=0, max_value=120),
    "email": StringField(pattern=r"^[^@]+@[^@]+\.[^@]+$")
})

# Validate data
data = {
    "name": "Alice Johnson",
    "age": 28,
    "email": "alice@example.com"
}

try:
    result = schema.validate(data)
    print("Validation successful:", result)
except ValidationError as e:
    print("Validation failed:", e)
```

### Nested Structures

```python
from schemafied import Schema, DictField, ListField, NumberField, StringField

# Complex nested schema
user_schema = Schema({
    "user_id": NumberField(min_value=1),
    "profile": DictField({
        "personal": DictField({
            "name": StringField(min_length=1, max_length=100),
            "age": NumberField(min_value=13, max_value=120)
        }),
        "preferences": DictField({
            "theme": StringField(required=False, default="light"),
            "notifications": ListField(
                StringField(max_length=20),
                required=False
            )
        }, required=False)
    }),
    "tags": ListField(
        StringField(min_length=1, max_length=20),
        max_length=10,
        required=False
    )
})

# Validate nested data
nested_data = {
    "user_id": 12345,
    "profile": {
        "personal": {
            "name": "Bob Smith",
            "age": 25
        },
        "preferences": {
            "theme": "dark",
            "notifications": ["email", "push"]
        }
    },
    "tags": ["python", "developer", "tech"]
}

result = user_schema.validate(nested_data)
```

## Field Types

### NumberField

Validates numeric values (int or float) with optional constraints.

```python
# Basic number validation
age = NumberField(min_value=0, max_value=120)

# Optional with default
score = NumberField(min_value=0, max_value=100, required=False, default=0)

# Custom validators
def must_be_even(value):
    return value % 2 == 0

even_number = NumberField(validators=[must_be_even])
```

**Parameters:**

- `min_value`: Minimum allowed value (inclusive)
- `max_value`: Maximum allowed value (inclusive)
- `required`: Whether field is required (default: True)
- `default`: Default value if field is missing
- `validators`: List of custom validation functions
- `coerce`: Enable type coercion from strings (default: True)

### StringField

Validates string values with length and pattern constraints.

```python
# Basic string validation
name = StringField(min_length=1, max_length=50)

# Pattern validation (regex)
email = StringField(pattern=r"^[^@]+@[^@]+\.[^@]+$")

# Optional with default
status = StringField(required=False, default="active")
```

**Parameters:**

- `min_length`: Minimum string length
- `max_length`: Maximum string length
- `pattern`: Regex pattern (string or compiled Pattern)
- `required`: Whether field is required (default: True)
- `default`: Default value if field is missing
- `validators`: List of custom validation functions
- `coerce`: Enable type coercion to string (default: True)

### ListField

Validates lists with item type validation and length constraints.

```python
# List of strings
tags = ListField(StringField(max_length=20), max_length=10)

# List of numbers with constraints
scores = ListField(
    NumberField(min_value=0, max_value=100),
    min_length=1,
    max_length=50
)

# Nested list validation
contacts = ListField(
    DictField({
        "type": StringField(),
        "value": StringField(min_length=1)
    }),
    max_length=5
)
```

**Parameters:**

- `item_field`: Field instance for validating list items
- `min_length`: Minimum list length
- `max_length`: Maximum list length
- `max_item_errors`: Maximum item errors to report (default: 10)
- `required`: Whether field is required (default: True)
- `coerce`: Enable coercion from iterables (default: True)

### DictField

Validates nested dictionaries against a sub-schema.

```python
# Nested dictionary validation
address = DictField({
    "street": StringField(min_length=1),
    "city": StringField(min_length=1),
    "postal_code": StringField(pattern=r"^\d{5}$"),
    "country": StringField(required=False, default="US")
})

# Strict mode (reject extra fields)
strict_config = DictField({
    "api_key": StringField(min_length=1),
    "timeout": NumberField(min_value=1, max_value=300)
}, strict=True)
```

**Parameters:**

- `schema`: Dictionary mapping field names to Field instances
- `strict`: Reject dictionaries with extra fields (default: False)
- `required`: Whether field is required (default: True)
- `coerce`: Enable coercion from dict-like objects (default: True)

## Error Handling

Schemafied provides detailed error information with exact field paths:

### Single Error

```python
from schemafied.exceptions import ValidationError

try:
    schema.validate(invalid_data)
except ValidationError as e:
    print(f"Error at {e.field_path}: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"Invalid value: {e.value}")
```

### Multiple Errors

```python
from schemafied.exceptions import ValidationErrorCollection

try:
    schema.validate(invalid_data)
except ValidationErrorCollection as e:
    print(f"Found {len(e.errors)} validation errors:")

    # Group errors by field
    for field_path, field_errors in e.get_errors_by_field().items():
        print(f"  {field_path}:")
        for error in field_errors:
            print(f"    - {error.message}")
```

### Partial Validation

Get validation results even when there are errors:

```python
result = schema.validate_partial(data)

if result['is_valid']:
    print("Data is valid:", result['data'])
else:
    print("Validation errors:", result['errors'])
    print("Partial data:", result['data'])
```

## Custom Validators

Create custom validation logic:

```python
def must_be_positive(value):
    """Custom validator that ensures value is positive."""
    if value <= 0:
        return "Value must be positive"
    return True

def must_be_even(value):
    """Custom validator using exceptions."""
    if value % 2 != 0:
        raise ValueError("Value must be even")
    return True

# Use in fields
positive_number = NumberField(
    min_value=1,
    validators=[must_be_positive, must_be_even]
)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
