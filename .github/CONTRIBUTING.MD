# Contributing to Schemafied

Thank you for your interest in contributing to Schemafied! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a harassment-free environment
- Support fellow contributors

## Getting Started

### Prerequisites

- Python 3.13+ (recommended: latest stable version)
- Git
- Basic understanding of Python Programming Language and it's associated concetps
- Familiarity with what this project's intent is and how it works

### First Contribution Ideas

- Fix typos in documentation
- Add examples to the README
- Improve error messages
- Add new field types
- Enhance test coverage

## Development Setup

1. **Fork and clone the repository:**

```bash
git clone https://github.com/devnadeemashraf/schemafied.git
cd schemafied
```

2. **Create a virtual environment:**

```bash
python -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate
```

3. **Install development dependencies:**

```bash
make install
# or manually:
pip install -r requirements.txt
```

4. **Verify setup:**

```bash
make test
```

## Contributing Process

### 1. Issue First

For significant changes:

- Open an issue first to discuss the proposed change
- Get feedback from maintainers/project owners before starting work
- Reference the issue in your pull request

### 2. Branch Naming

Use descriptive branch names, examples:

- `feature/add-boolean-field`
- `fix/list-validation-error`
- `docs/update-api-reference`
- `test/improve-coverage`

### 3. Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Detailed explanation of the change
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test improvements
- `refactor`: Code refactoring
- `style`: Code style changes
- `update`: Minor non-breaking changes
- `chore`: Maintenance tasks

**Examples:**

```
feat(fields): add BooleanField with validation support

- Implements boolean type validation
- Supports true/false string coercion
- Includes comprehensive test coverage

fix(validation): correct nested error path construction

Fixes issue where nested dictionary paths were not
properly constructed when validation errors occurred
in deeply nested structures.
```

## Coding Standards

### Python Style

- Follow **PEP 8** style guidelines
- Use **type hints** for all public methods
- Maximum line length: **88 characters** (Black formatter)
- Use **descriptive variable names**

### Code Quality Tools

Run before submitting:

```bash
make prepare    # Perform all checks (format, lint, test)
```

or you can run individual commands:

```bash
make format     # Format code with Black
make lint       # Check with flake8
make test       # Run all tests
```

### Architecture Principles

1. **Declarative Design**: Keep validation rules clear and readable
2. **Error Aggregation**: Collect all errors, don't fail fast
3. **Extensibility**: Design for easy extension and customization
4. **Type Safety**: Use type hints throughout
5. **Performance**: Consider performance implications for large datasets

### Field Implementation Guidelines

When adding new field types:

```python
from typing import Any
from .base import Field
from ..validation_context import ValidationContext
from ..exceptions import ValidationError, TypeValidationError

class NewField(Field):
    """Field for validating [description]."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Field-specific initialization

    def _validate_type(self, value: Any, context: ValidationContext) -> Any:
        """Validate and coerce the value."""
        # 1. Type validation with coercion
        # 2. Constraint validation
        # 3. Return validated value
        pass
```

### Error Handling Standards

- Use appropriate exception types (`ConstraintError`, `TypeValidationError`, etc.)
- Provide clear, actionable error messages
- Include field paths in error context
- Support both single and multiple error scenarios

## Testing Guidelines

### Test Structure

Tests are organized by component:

- `tests/test_schema.py` - Schema validation tests
- `tests/test_fields.py` - Individual field tests
- `tests/test_integration.py` - End-to-end tests
- `tests/test_error_handling.py` - Error handling tests

### Writing Tests

1. **Test both success and failure cases**
2. **Use descriptive test names**
3. **Test edge cases and invalid inputs**
4. **Verify error messages and field paths**

```python
def test_number_field_constraint_validation(self):
    """Test NumberField properly validates min/max constraints."""
    field = NumberField(min_value=10, max_value=20)
    context = ValidationContext("test_field")

    # Test valid value
    result = field.validate(15, context)
    self.assertEqual(result, 15)
    self.assertFalse(context.has_errors())

    # Test invalid value
    context_invalid = ValidationContext("test_field")
    field.validate(5, context_invalid)
    self.assertTrue(context_invalid.has_errors())

    error = context_invalid.errors[0]
    self.assertIsInstance(error, ConstraintError)
    self.assertIn("at least 10", error.message)
```

### Test Coverage

- Aim for **70%+ code coverage**
- Focus on edge cases, critical paths and error conditions
- Test performance with large datasets
- Include integration tests for real-world scenarios

### Running Tests

```bash
# All tests
make test

# Specific test file
make test-file FILE=test_fields.py

# With coverage
make test-coverage

# Verbose output
make test-verbose
```

## Documentation

### Code Documentation

- **Docstrings** for all public classes and methods
- **Type hints** for method signatures
- **Examples** in docstrings for complex functionality

```python
def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data against this schema.

    Args:
        data: Dictionary to validate

    Returns:
        Validated dictionary with coerced values

    Raises:
        ValidationError: Single validation error
        ValidationErrorCollection: Multiple validation errors

    Example:
        >>> schema = Schema({"name": StringField()})
        >>> result = schema.validate({"name": "Alice"})
        >>> print(result)
        {"name": "Alice"}
    """
```

### README Updates

When adding new features:

- Update relevant sections
- Add examples
- Update API reference
- Maintain accuracy

## Issue Reporting

### Bug Reports

Include:

- **Python version** and operating system
- **Schemafied version**
- **Complete error traceback**
- **Minimal reproduction example**
- **Expected vs actual behavior**

### Feature Requests

Include:

- **Use case description**
- **Proposed API design**
- **Alternative solutions considered**
- **Implementation willingness**

### Issue Templates

Use the provided issue templates when available.

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**: `make test`
2. **Run code quality checks**: `make dev-check`
3. **Update documentation** if needed
4. **Add changelog entry** for user-facing changes
5. **Test with real-world scenarios**

### PR Description

Include:

- **Summary** of changes
- **Issue reference** (if applicable)
- **Breaking changes** (if any)
- **Testing** performed
- **Documentation** updates

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in different environments
4. **Documentation** review
5. **Final approval** and merge

### After Merge

- **Monitor** for any issues
- **Respond** to follow-up questions
- **Celebrate** your contribution! 🎉

## Development Workflow Example

```bash
# 1. Create feature branch
git checkout -b feature/add-email-field

# 2. Implement changes
# ... code changes ...

# 3. Run development checks
make dev-check

# 4. Commit changes
git add .
git commit -m "feat(fields): add EmailField with validation"

# 5. Push and create PR
git push origin feature/add-email-field
# Create PR through GitHub interface

# 6. Address review feedback
# ... make changes based on review ...

# 7. Final checks before merge
make ci
```

## Getting Help

- **Documentation**: Check the README and API docs first
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: Reach out to maintainers for guidance

## Recognition

Contributors are recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **Git history** as permanent record

Thank you for contributing to Schemafied! Your efforts help make dictionary validation better for everyone.
