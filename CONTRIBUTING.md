# Contributing to AVM Action

Thank you for your interest in contributing to `avm-action`! This document provides guidelines for contributing.

## Quick Start

1. **Fork and clone** the repository
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r .github/actions/avm-action/requirements-dev.txt
   ```
4. **Make your changes** on a feature branch
5. **Run tests and linting**:
   ```bash
   pytest tests/ -v
   black --check .github/actions/avm-action/src/ tests/
   ruff check .github/actions/avm-action/src/ tests/
   ```
6. **Submit a pull request**

## Development Guidelines

### Code Style

- **Python**: Use `black` for formatting, `ruff` for linting
- **Type Hints**: Required for all function signatures
- **Docstrings**: Use Google-style docstrings
- **Terraform**: Use `terraform fmt`

### Testing

- Write tests for all new functionality
- Maintain or improve code coverage
- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(config): add support for multiple workspaces
fix(runner): handle missing terraform binary
docs(readme): update installation instructions
```

### Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure CI checks pass
4. Request review from maintainers
5. Address feedback promptly

## Detailed Guidelines

For more detailed information, see [docs/contributing-guidelines.md](docs/contributing-guidelines.md).

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Questions?

- Open a [GitHub Issue](https://github.com/Action-Foundry/AVM-Action/issues) for bugs
- Start a [Discussion](https://github.com/Action-Foundry/AVM-Action/discussions) for questions

Thank you for contributing! 🎉
