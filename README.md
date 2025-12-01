# AVM Action

[![CI](https://github.com/Action-Foundry/AVM-Action/actions/workflows/ci.yml/badge.svg)](https://github.com/Action-Foundry/AVM-Action/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-based GitHub Action for working with Terraform in **Azure Verified Modules (AVM)**-style environments.

## Overview

`avm-action` provides a clean, opinionated interface for Terraform workflows, designed for enterprise use with Azure infrastructure. It supports:

- **Docker-based Execution**: Self-contained environment with Terraform pre-installed
- **Terraform Commands**: `init`, `validate`, `plan`, `apply`, `destroy`
- **Multiple tfvars files**: Pass environment-specific configurations
- **Workspace Management**: Automatic workspace selection and creation
- **Azure Authentication**: OIDC, Service Principal, and CLI authentication support
- **Variable Overrides**: Pass variables via JSON or key=value pairs

## Quick Start

### Basic Usage

```yaml
name: Terraform Plan

on:
  pull_request:
    branches: [main]

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Terraform Plan
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform
          command: plan
          tfvars_files: terraform.tfvars
```

> **Note**: The action includes Terraform in the Docker container, so you don't need to use `hashicorp/setup-terraform` separately.

### With Azure Authentication (OIDC)

```yaml
name: Terraform Apply

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  apply:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Terraform Apply
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform
          command: apply
          tfvars_files: production.tfvars
          workspace: production
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `tf_directory` | Path to Terraform configuration | No | `.` |
| `tfvars_files` | Comma-separated list of tfvars files | No | `""` |
| `backend_config_file` | Path to backend configuration | No | `""` |
| `command` | Terraform command to run | Yes | `plan` |
| `workspace` | Terraform workspace | No | `default` |
| `azure_subscription_id` | Azure Subscription ID | No | `""` |
| `azure_tenant_id` | Azure Tenant ID | No | `""` |
| `azure_client_id` | Azure Client ID | No | `""` |
| `var_overrides` | JSON or key=value variable overrides | No | `""` |
| `log_level` | Logging level | No | `INFO` |
| `avm_version` | Azure Verified Modules version | No | `latest` |
| `terraform_version` | Terraform version | No | `latest` |
| `azurerm_version` | Azure RM provider version | No | `latest` |

## Outputs

| Output | Description |
|--------|-------------|
| `plan_output` | Output from terraform plan |
| `state_summary` | Summary of state changes |

## Documentation

- [Action Usage Guide](docs/action-usage.md) - Detailed usage examples and patterns
- [Terraform Usage Guide](docs/terraform-usage.md) - Structuring Terraform for AVM
- [Architecture](docs/architecture.md) - Design decisions and extension points
- [Contributing Guidelines](docs/contributing-guidelines.md) - Development setup and standards

## Repository Structure

```
.
├── .github/
│   ├── actions/avm-action/     # GitHub Action implementation
│   │   ├── action.yml          # Action metadata
│   │   ├── Dockerfile          # Docker image definition
│   │   ├── entrypoint.sh       # Container entrypoint script
│   │   ├── src/                # Python source code
│   │   ├── requirements.txt    # Runtime dependencies
│   │   └── requirements-dev.txt # Development dependencies
│   └── workflows/              # CI/CD workflows
├── terraform/
│   ├── modules/                # Reusable Terraform modules
│   └── examples/               # Example configurations
├── docs/                       # Documentation
└── tests/                      # Unit and integration tests
```

## Development

### Prerequisites

- Python 3.11+
- Docker (for local testing)
- Terraform 1.3.0+ (optional, included in Docker image)

### Setup

```bash
# Install dependencies
pip install -r .github/actions/avm-action/requirements-dev.txt

# Run tests
pytest tests/ -v --cov

# Run linting
black --check .github/actions/avm-action/src/ tests/
ruff check .github/actions/avm-action/src/ tests/
```

### Docker Build

```bash
# Build the action Docker image
docker build -t avm-action:local .github/actions/avm-action/

# Test the Docker image
docker run --rm --entrypoint terraform avm-action:local version
```

### Terraform Validation

```bash
cd terraform/examples/basic-usage
terraform init
terraform validate
```

## Contributing

We welcome contributions! Please see:
- [CONTRIBUTING.md](CONTRIBUTING.md) for quick start
- [docs/contributing-guidelines.md](docs/contributing-guidelines.md) for detailed guidelines

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/) for AVM patterns
- [HashiCorp Terraform](https://www.terraform.io/) for infrastructure as code
