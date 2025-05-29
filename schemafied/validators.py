class CustomValidator:
    def __init__(self, validation_func) -> None:
        self.validation_func = validation_func

    def validate(self, value: any) -> any:
        return self.validation_func(value)


def validate_positive(value: int | float) -> int | float:
    if value <= 0:
        raise ValueError("Value must be positive.")
    return value


def validate_non_empty_string(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Value must be a non-empty string.")
    return value


def validate_email(value: str) -> str:
    import re

    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise ValueError("Value must be a valid email address.")
    return value


def validate_custom_field(value: any, validators) -> any:
    errors = []
    for validator in validators:
        try:
            validator.validate(value)
        except ValueError as e:
            errors.append(str(e))
    if errors:
        raise ValueError("Validation errors: " + ", ".join(errors))
    return value
