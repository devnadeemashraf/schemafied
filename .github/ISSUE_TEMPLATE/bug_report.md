---
name: Bug Report
about: Create a report to help us improve Schemafied
title: "[BUG] "
labels: bug
assignees: ""
---

## Bug Description

**A clear and concise description of what the bug is.**

## Expected Behavior

**What you expected to happen.**

## Actual Behavior

**What actually happened.**

## Minimal Reproduction Example

```python
# Please provide a minimal, complete example that reproduces the issue
from schemafied import Schema, NumberField, StringField

# Your schema definition
schema = Schema({
    # ... your fields
})

# The data that causes the issue
data = {
    # ... your test data
}

# The validation call that fails
result = schema.validate(data)  # This should work but doesn't
```

## Error Output

```
Please paste the complete error message and stack trace here
```

## Environment Information

- **Schemafied Version:** [e.g., 1.0.0]
- **Python Version:** [e.g., 3.9.2]
- **Operating System:** [e.g., Windows 10, macOS 12.0, Ubuntu 20.04]
- **Installation Method:** [e.g., pip, conda, from source]

## Context and Use Case

**Describe what you're trying to accomplish and why this behavior is problematic for your use case.**

## Additional Context

**Add any other context about the problem here. Include:**

- Schema complexity (number of fields, nesting levels)
- Data size (if relevant)
- Performance expectations
- Any workarounds you've tried

## Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have provided a minimal reproduction example
- [ ] I have included the complete error message
- [ ] I have specified my environment details
