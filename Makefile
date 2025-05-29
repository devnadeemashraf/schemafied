.PHONY: help clean test build prepare upload-test upload release install-dev verify-version verify-build verify-package

# Default target
help:
	@echo "Essential Schemafied Commands:"
	@echo "  clean          - Remove cache and build artifacts"
	@echo "  test           - Run all tests"
	@echo "  install-dev    - Install development dependencies"
	@echo "  verify-version - Verify package version is set correctly"
	@echo "  verify-build   - Verify built packages are correct"
	@echo "  verify-package - Complete package verification"
	@echo "  build          - Build distribution packages"
	@echo "  upload-test    - Upload to test PyPI"
	@echo "  upload         - Upload to production PyPI"
	@echo "  release        - Complete release workflow"
	@echo ""
	@echo "Development:"
	@echo "  prepare        - Prepare the code for version control push"
	@echo "  format         - Format code with black"
	@echo "  lint           - Lint code with flake8"
	@echo "  dev-check      - Run all quality checks"

# Clean cache and build artifacts
clean:
	@echo "Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ .coverage htmlcov/ dist/ build/ *.egg-info/ .mypy_cache/ schemafied/*.egg-info/
	@echo "Clean complete!"

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements-dev.txt
	pip install -e .
	@echo "Installation complete!"

# Code quality - SIMPLE COMMANDS ONLY
format:
	@echo "Formatting code..."
	black schemafied/ tests/ --line-length 240

lint:
	@echo "Linting code..."
	flake8 schemafied/ tests/ --max-line-length=240 --extend-ignore=E203,W503,F821

test:
	@echo "Running tests..."
	python -m pytest tests/ -v


prepare: format lint test
	@echo "Preparation complete! Code is formatted, linted, and tested."

dev-check: clean prepare
	@echo "All development checks passed!"
	
# Verification commands - IMPLEMENTATIONS MOVED TO SCRIPTS
verify-version:
	@echo "=== Verifying Package Version ==="
	@python scripts/verify_version.py

verify-build:
	@echo "=== Verifying Build Artifacts ==="
	@python scripts/verify_build.py

verify-package: verify-version verify-build
	@echo "=== Verifying Package with Twine ==="
	python -m twine check dist/*
	@echo "Package verification passed"

# Version Management Commands
version-check:
	@echo "=== Current Version Status ==="
	@echo -n "Current version: "
	@grep "__version__" schemafied/__init__.py | cut -d'"' -f2
	@echo -n "Latest Git tag: "
	@git describe --tags --abbrev=0 2>/dev/null || echo "No tags found"
	@echo "Git status:"
	@git status --porcelain || echo "  Clean working directory"
	@echo ""

# Build process
build: clean dev-check verify-version
	@echo "=== Building Distribution Packages ==="
	python -m build
	@$(MAKE) verify-build
	@$(MAKE) verify-package
	@echo "Build complete and verified!"

# Upload commands - IMPLEMENTATION MOVED TO SCRIPTS
upload-test: build
	@echo "=== Uploading to Test PyPI ==="
	@python scripts/upload_info.py test
	python -m twine upload --repository testpypi dist/* --verbose
	@python scripts/upload_success.py test

upload: build
	@echo "=== Uploading to Production PyPI ==="
	@python scripts/upload_info.py prod
	python -m twine upload dist/* --verbose
	@python scripts/upload_success.py prod

release: upload
	@echo "Release Complete!"
	@python scripts/release_info.py