class CustomValidator:
    def __init__(self, validation_func):
        self.validation_func = validation_func

    def validate(self, value):
        return self.validation_func(value)


def validate_positive(value):
    if value <= 0:
        raise ValueError("Value must be positive.")
    return value


def validate_non_empty_string(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Value must be a non-empty string.")
    return value


def validate_email(value):
    import re

    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise ValueError("Value must be a valid email address.")
    return value


def validate_custom_field(value, validators):
    errors = []
    for validator in validators:
        try:
            validator.validate(value)
        except ValueError as e:
            errors.append(str(e))
    if errors:
        raise ValueError("Validation errors: " + ", ".join(errors))
    return value
