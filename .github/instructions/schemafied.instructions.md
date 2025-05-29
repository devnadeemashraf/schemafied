---
applyTo: "**"
---

# Schemafied - Custom Python Dictionary Validation Library

## Project Overview

Schemafied is a Python library for validating data structures against user-defined schemas with comprehensive error reporting and nested structure support. It enables developers to create complex validation schemas for nested dictionaries with granular validation rules, type coercion, and custom field types.

## Core Architecture

### Design Principles

- **Declarative Schema Definition**: Users define schemas using field instances in a clear, readable manner
- **Comprehensive Error Aggregation**: Collect all validation errors instead of failing fast, with precise field paths
- **Extensible Field System**: Support for custom field types and validators with consistent API patterns
- **Nested Structure Support**: Handle complex nested dictionaries and lists with performance optimization
- **Type Coercion**: Allow safe type conversion where appropriate (strings to numbers, etc.)
- **Error Limiting**: Prevent memory issues with large datasets by limiting error collection
- **Type Safety**: Full type hint support for better developer experience

### Key Components

1. **Schema Class**: Root validation container that orchestrates field validation
2. **Field Base Class**: Abstract base for all field types with common validation logic
3. **Built-in Field Types**:
   - `NumberField`: Numeric validation with min/max constraints and coercion
   - `StringField`: String validation with length/pattern constraints
   - `DictField`: Nested dictionary validation with sub-schemas and strict mode
   - `ListField`: List validation with item type validation and length constraints
4. **Error Handling**: Structured error aggregation with detailed field paths and error codes
5. **Custom Validators**: Function-based custom validation with flexible return types
6. **Partial Validation**: Continue validation even with errors for better UX

## Directory Structure

```
schemafied/
├── src/
│   ├── __init__.py              # Main package exports (Schema, all Fields, exceptions)
│   ├── schema.py                # Schema class with validate() and validate_partial()
│   ├── validation_context.py    # ValidationContext for hierarchical error tracking
│   ├── exceptions.py            # ValidationError, ValidationErrorCollection, specific error types
│   ├── validators.py            # Utility functions for custom validators
│   └── fields/
│       ├── __init__.py          # Field exports (NumberField, StringField, etc.)
│       ├── base.py              # Base Field class with validation framework
│       ├── number.py            # NumberField with numeric constraints
│       ├── string.py            # StringField with length/pattern validation
│       ├── dict.py              # DictField with nested schema support
│       └── list.py              # ListField with item validation
├── tests/
│   ├── __init__.py              # Test package initialization
│   ├── test_schema.py           # Schema validation and error aggregation tests
│   ├── test_fields.py           # Individual field type tests
│   ├── test_integration.py      # End-to-end complex schema tests
│   ├── test_performance.py      # Large dataset and error limiting tests
│   ├── test_error_handling.py   # Comprehensive error handling tests
│   └── test_edge_cases.py       # Edge cases and unusual scenarios
├── scripts/
│   ├── verify_version.py        # Script that verifies the version of the library
│   ├── verify_build.py          # Script that verifies the build artifacts
│   ├── release_info.py          # Release completion information
│   ├── upload_info.py           # Upload start messages
│   └── upload_success.py        # Upload success messages
└── requirements.txt             # No External Runtime Dependencies
└── requirements-dev.txt         # Development Dependencies
```

## LLM Response Guidelines

### Response Philosophy

**TEACH, DON'T IMPLEMENT**: The primary goal is to guide users toward understanding the architecture and making informed implementation decisions, not to provide complete code solutions. If there are more than one questions asked and the response also has multiple parts, always break them out into multiple responses and wait for user's clarifiaction before moving on to the next part. Also, mention whenever this is the case so that the user is aware of it.

### Response Structure

1. **Conceptual Explanation** (30-40% of response)

   - Explain the underlying concepts and why they matter
   - Reference existing patterns in the codebase
   - Connect to the overall architecture

2. **Pseudo-code or High-level Structure** (40-50% of response)

   - Show the logical flow and key decision points
   - Indicate where existing components should be used
   - Highlight extension points and customization opportunities

3. **Specific Implementation Hints** (10-20% of response)
   - Point to specific files/classes that need modification
   - Suggest method signatures or class structures
   - Identify potential pitfalls or edge cases

### Code Guidance Patterns

#### When Explaining Field Implementation:

```pseudo
# DON'T provide complete implementation
# DO provide exact paths to the files where updates should be made
# DO explain the purpose of each method
# DO provide hints for some complex or unconventional logics/implementations
# DO provide structure like this:

class CustomField(Field):
    def __init__(self, custom_param, **kwargs):
        # Initialize custom parameters
        # Call parent __init__ with base parameters
        # Store validation state

    def _validate_type(self, value, path):
        # 1. Check if value matches expected type
        # 2. Apply coercion if enabled and possible
        # 3. Return coerced value or raise ValidationError

    def _validate_constraints(self, value, path):
        # 1. Apply field-specific constraints
        # 2. Run custom validators if provided
        # 3. Collect errors using self._add_error()
        # 4. Return validated value
```

#### When Explaining Error Handling:

```pseudo
# Structure for error aggregation:
errors = []
try:
    # Validate each field
    # Continue even if individual fields fail
except ValidationError as e:
    errors.append(e)

if errors:
    # Decide: single error or collection
    # Consider error limiting for performance
    # Provide clear field paths
```

#### When Discussing Schema Composition:

```pseudo
# Pattern for nested validation:
def validate_nested_structure(self, data, base_path=""):
    # 1. Iterate through schema fields
    # 2. Extract field value from data
    # 3. Construct field path: f"{base_path}.{field_name}"
    # 4. Delegate to field.validate(value, field_path)
    # 5. Aggregate results and errors
```

### Explanation Depth Guidelines

#### Shallow Explanations (1-2 sentences):

- Basic field usage and parameters
- Standard validation patterns
- Common error scenarios

#### Medium Explanations (3-5 sentences):

- Custom validator implementation
- Error aggregation strategies
- Type coercion logic
- Performance considerations

#### Deep Explanations (6+ sentences):

- Complex nested schema design
- Custom field type architecture
- Error limiting and memory management
- Schema inheritance and composition
- Extension point design

### Reference Standards

#### File Path References:

Always use the exact file structure:

- `src/fields/base.py` for Field base class
- `src/exceptions.py` for error classes
- `src/schema.py` for Schema implementation
- `src/validation_context.py` for ValidationContext
- `tests/test_*.py` for test examples

#### API Consistency:

- All fields inherit from `Field` base class
- Constructor pattern: `FieldType(constraints..., required=True, default=None, validators=[])`
- Validation method: `field.validate(value, path="field_name")`
- Error creation: `ValidationError(message, field_path, error_code, value)`

#### Error Code Standards:

- `INVALID_TYPE` - Type mismatch errors
- `CONSTRAINT_VIOLATION` - Field constraint failures
- `REQUIRED_FIELD` - Missing required fields
- `CUSTOM_VALIDATION` - Custom validator failures

### Learning-Focused Responses

#### Encourage Exploration:

- "Consider how this pattern extends to other field types..."
- "Think about the trade-offs between performance and error detail..."
- "This approach mirrors the pattern used in `existing_file.py`..."

#### Provide Context:

- Reference the README examples for user-facing API
- Connect implementation details to the documented features
- Explain why certain design decisions were made

#### Guide Problem-Solving:

```pseudo
# Instead of: "Here's the complete solution"
# Provide: "Here's the approach you should take"

# 1. First, understand the problem space
# 2. Then, identify which components need modification
# 3. Consider how your changes affect error handling
# 4. Think about edge cases and performance
# 5. Test with both valid and invalid data
```

### Pseudo-code Standards

Use clear, language-agnostic pseudo-code that shows:

- Logical flow and decision points
- Key method calls and class interactions
- Error handling strategies
- Data transformation steps

```pseudo
# Good pseudo-code example:
function validate_list_field(items, item_field, constraints):
    validated_items = []
    errors = []

    for index, item in enumerate(items):
        item_path = f"{base_path}[{index}]"
        try:
            validated_item = item_field.validate(item, item_path)
            validated_items.append(validated_item)
        except ValidationError as error:
            errors.append(error)
            if len(errors) >= max_item_errors:
                break

    return validated_items, errors
```

### Testing and Validation Guidance

#### Test Structure Recommendations:

- Unit tests for each field type in isolation
- Integration tests for complex nested schemas
- Performance tests for large datasets
- Edge case tests for error conditions

#### Example-Driven Explanations:

Reference examples from the README and test files to show real-world usage patterns.

### Extension and Customization Guidance

#### Custom Field Development:

Point users toward the base Field class and explain the key methods they need to implement rather than providing complete implementations.

#### Custom Validator Patterns:

Explain the function signature and return value expectations rather than writing the validators.

This instruction set ensures that LLM responses focus on teaching architectural understanding and guiding implementation decisions rather than providing complete code solutions, fostering deeper learning and better code ownership.
