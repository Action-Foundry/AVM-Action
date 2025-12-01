# Architecture

This document describes the high-level architecture and design decisions for the `avm-action` GitHub Action.

## Overview

`avm-action` is a Python-based GitHub Action designed to provide a clean, opinionated interface for Terraform workflows in Azure Verified Modules (AVM) environments.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     action.yml                              │ │
│  │  (Composite Action - orchestrates Python execution)        │ │
│  └─────────────────────────┬──────────────────────────────────┘ │
│                            │                                     │
│  ┌─────────────────────────▼──────────────────────────────────┐ │
│  │                     src/main.py                             │ │
│  │  (Entry point - orchestrates action execution)             │ │
│  └─────────────────────────┬──────────────────────────────────┘ │
│                            │                                     │
│        ┌───────────────────┼───────────────────┐                │
│        │                   │                   │                │
│        ▼                   ▼                   ▼                │
│  ┌──────────┐       ┌───────────────┐   ┌──────────────┐       │
│  │ config   │       │ terraform     │   │ azure_auth   │       │
│  │ .py      │       │ _runner.py    │   │ .py          │       │
│  └──────────┘       └───────────────┘   └──────────────┘       │
│                            │                                     │
│                            ▼                                     │
│                   ┌────────────────┐                            │
│                   │   Terraform    │                            │
│                   │   CLI          │                            │
│                   └────────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### action.yml

The composite action definition that:
- Declares inputs and outputs for the action
- Sets up the Python environment
- Installs dependencies
- Invokes the Python entry point

### src/main.py

The main entry point that orchestrates:
1. Configuration loading from environment
2. Validation of inputs
3. Terraform command construction
4. Command execution
5. Output setting for GitHub Actions

### src/config.py

Handles all configuration concerns:
- Parsing GitHub Action inputs from environment variables
- Type conversion (strings to lists, JSON to dicts)
- Default value application
- Validation logic

### src/terraform_runner.py

Manages Terraform command execution:
- Command construction for all Terraform operations
- Working directory management
- Output capture and parsing

### src/azure_auth.py

Provides Azure authentication abstraction:
- Detection of authentication method
- Credential management
- Environment variable setup for Terraform

### src/utils/

Shared utilities:
- `logging.py`: Logging setup and GitHub Actions output formatting

## Design Decisions

### Why Python + Composite Action?

1. **Flexibility**: Python provides rich libraries for parsing, validation, and subprocess management
2. **Testability**: Python is easily unit-testable with pytest
3. **Extensibility**: Adding new Terraform commands or features is straightforward
4. **Composite Actions**: Allow combining Python execution with other actions (like setup-python)

### Why Dataclasses for Configuration?

Dataclasses provide:
- Type hints for IDE support
- Automatic `__init__`, `__repr__`, and `__eq__`
- Easy serialization and validation
- Immutability options if needed

### Separation of Concerns

The codebase is organized to separate:
- **Input/Output** (config.py, utils/logging.py)
- **Business Logic** (terraform_runner.py)
- **External Integration** (azure_auth.py)

This makes each component independently testable and maintainable.

## Authentication Flow

### Current Implementation

```
┌─────────────────┐
│ GitHub Action   │
│ Inputs          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ AzureAuth       │────▶│ detect_auth     │
│ enticator       │     │ _method()       │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Authentication Method                    │
├─────────────────────────────────────────┤
│ ❌ OIDC (Not yet implemented)           │
│ ⚠️ Service Principal (Partial)          │
│ ❌ Managed Identity (Not yet implemented)│
│ ✅ CLI (Use `azure/login` first)        │
└─────────────────────────────────────────┘
```

### Planned OIDC Implementation

TODO: Implement full OIDC flow:

1. Request OIDC token from GitHub
2. Exchange with Azure AD for access token
3. Set ARM_OIDC_TOKEN environment variable
4. Enable ARM_USE_OIDC for Terraform

## Terraform Command Flow

```
┌─────────────────┐
│ config.command  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ TerraformRunner.build_command()         │
├─────────────────────────────────────────┤
│ • build_init_command()                  │
│ • build_validate_command()              │
│ • build_plan_command()                  │
│ • build_apply_command()                 │
│ • build_destroy_command()               │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Subprocess      │
│ Execution       │
└─────────────────┘
```

## Adding New Terraform Workflows

To add support for a new Terraform command:

1. Add the command to `TerraformCommand` enum in `config.py`
2. Create `build_<command>_command()` method in `TerraformRunner`
3. Add the builder to the `builders` dict in `build_command()`
4. Add unit tests for the new command
5. Update documentation

## Out of Scope (Deferred to Future PRs)

The following items are intentionally out of scope for the initial implementation:

### Authentication
- [ ] Full GitHub OIDC token exchange with Azure AD
- [ ] Managed Identity authentication support
- [ ] Certificate-based authentication

### Terraform Features
- [ ] Remote state locking
- [ ] Plan file storage and retrieval
- [ ] Terraform Cloud/Enterprise integration
- [ ] Module registry support

### Advanced Features
- [ ] Cost estimation integration
- [ ] Policy-as-code (OPA, Sentinel)
- [ ] Telemetry and metrics
- [ ] Custom provider caching

### CI/CD
- [ ] Reusable workflow templates
- [ ] Matrix strategy for multi-environment deployments
- [ ] Automated changelog generation

## Security Considerations

### Current Posture

- No secrets stored in repository
- All sensitive values passed via GitHub Action inputs
- Subprocess execution with controlled environment
- Dry-run mode for safe testing

### Planned Security Improvements

- [ ] Input sanitization for command injection prevention
- [ ] Secret masking in logs
- [ ] SBOM generation for dependencies
- [ ] Signed releases

## Dependencies

### Runtime
- Python 3.11+
- Terraform CLI (user-provided or via setup-terraform)

### Development
- pytest for testing
- black for formatting
- ruff for linting
- mypy for type checking

## Extension Points

The architecture provides several extension points:

1. **Custom Terraform Commands**: Extend `TerraformCommand` enum
2. **New Auth Methods**: Implement in `AzureAuthenticator`
3. **Additional Inputs**: Add to `action.yml` and `ActionConfig`
4. **Output Processing**: Extend `CommandResult` handling
5. **Logging Integrations**: Add to `utils/logging.py`

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup and contribution guidelines.
