# Contributing Guidelines

This document provides extended guidelines for contributing to the `avm-action` project.

## Development Environment

### Prerequisites

- Python 3.11 or later
- Docker (for testing the action locally)
- Terraform 1.3.0 or later (optional, included in Docker image)
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Action-Foundry/AVM-Action.git
   cd AVM-Action
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate   # Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -r .github/actions/avm-action/requirements-dev.txt
   ```

4. Build the Docker image:
   ```bash
   docker build -t avm-action:local .github/actions/avm-action/
   ```

## Code Style

### Python

We follow these conventions:

- **Formatting**: Use `black` with default settings
- **Linting**: Use `ruff` for linting
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings

Example:
```python
def calculate_total(items: list[float], tax_rate: float = 0.0) -> float:
    """Calculate the total price including tax.

    Args:
        items: List of item prices.
        tax_rate: Tax rate as a decimal (e.g., 0.1 for 10%).

    Returns:
        Total price including tax.

    Raises:
        ValueError: If tax_rate is negative.
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

### Terraform

- Use `terraform fmt` for formatting
- Follow [Azure naming conventions](https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/naming-and-tagging)
- Include validation blocks for variables
- Document all modules with README.md

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=.github/actions/avm-action/src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py -v

# Run tests matching a pattern
pytest tests/ -k "test_validate" -v
```

### Writing Tests

Tests should:
- Be placed in `tests/unit/` or `tests/integration/`
- Follow the naming convention `test_<module>.py`
- Use pytest fixtures for common setup
- Cover edge cases and error conditions

Example:
```python
import pytest
from src.config import ActionConfig

class TestActionConfig:
    @pytest.fixture
    def valid_config(self):
        return ActionConfig(
            tf_directory="./terraform",
            command=TerraformCommand.PLAN
        )

    def test_validate_returns_no_errors_for_valid_config(self, valid_config):
        errors = valid_config.validate()
        assert errors == []

    def test_validate_catches_empty_directory(self):
        config = ActionConfig(tf_directory="")
        errors = config.validate()
        assert "tf_directory cannot be empty" in errors
```

## Linting and Formatting

### Python

```bash
# Format code
black .github/actions/avm-action/src/
black tests/

# Check formatting (CI mode)
black --check .github/actions/avm-action/src/ tests/

# Lint code
ruff check .github/actions/avm-action/src/ tests/

# Fix auto-fixable issues
ruff check --fix .github/actions/avm-action/src/ tests/

# Type checking
mypy .github/actions/avm-action/src/
```

### Docker

```bash
# Build the Docker image
docker build -t avm-action:local .github/actions/avm-action/

# Test the Docker image runs
docker run --rm --entrypoint terraform avm-action:local version

# Test the action with a local Terraform configuration
docker run --rm \
  -e INPUT_TF_DIRECTORY="." \
  -e INPUT_COMMAND="validate" \
  -e INPUT_LOG_LEVEL="DEBUG" \
  -v $(pwd)/terraform/examples/basic-usage:/github/workspace \
  -w /github/workspace \
  avm-action:local
```

### Terraform

```bash
# Format all Terraform files
terraform fmt -recursive terraform/

# Check formatting
terraform fmt -check -recursive terraform/

# Validate configurations
cd terraform/examples/basic-usage
terraform init
terraform validate
```

## Git Workflow

### Branch Naming

- `feature/<description>` - New features
- `fix/<description>` - Bug fixes
- `docs/<description>` - Documentation changes
- `refactor/<description>` - Code refactoring
- `test/<description>` - Test additions or changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Refactoring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(config): add support for multiple tfvars files

fix(runner): handle missing terraform binary gracefully

docs(readme): add usage examples for OIDC authentication
```

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with appropriate commits
3. Ensure all tests pass locally
4. Update documentation if needed
5. Open a pull request
6. Address review feedback
7. Squash and merge when approved

### Pull Request Template

Your PR description should include:
- Summary of changes
- Related issue (if any)
- Testing performed
- Checklist:
  - [ ] Tests added/updated
  - [ ] Documentation updated
  - [ ] Linting passes
  - [ ] No security vulnerabilities introduced

## Adding New Features

### Adding a New Terraform Command

1. Add to `TerraformCommand` enum in `src/config.py`
2. Create `build_<command>_command()` in `TerraformRunner`
3. Add to `builders` dict in `build_command()`
4. Write unit tests
5. Update documentation

### Adding a New Action Input

1. Add to `action.yml` inputs section
2. Add to `ActionConfig` dataclass
3. Update `load_config_from_env()` parsing
4. Add validation if needed
5. Write unit tests
6. Update action README and docs

## Security

### Reporting Vulnerabilities

See [SECURITY.md](../SECURITY.md) for security policy and reporting procedures.

### Security Practices

- Never commit secrets
- Use GitHub Secrets for sensitive values
- Validate and sanitize all inputs
- Keep dependencies updated
- Run security scanning in CI

## Getting Help

- Open an issue for bugs or feature requests
- Use discussions for questions
- Tag maintainers for urgent issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
