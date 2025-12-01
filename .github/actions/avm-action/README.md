# AVM Action

A Python-based GitHub Action for working with Terraform in Azure Verified Modules (AVM)-style environments.

## Purpose

This action provides a clean, opinionated interface for Terraform workflows (`init`, `plan`, `apply`, `destroy`) in Azure environments. It is designed to work seamlessly with AVM (Azure Verified Modules) patterns.

## Features

- **Terraform Command Execution**: Run `init`, `validate`, `plan`, `apply`, and `destroy` commands
- **tfvars Support**: Accept multiple tfvars files via comma-separated list
- **Workspace Management**: Automatic workspace selection/creation
- **Azure Authentication**: Support for OIDC, Service Principal, and CLI authentication (partial implementation)
- **Variable Overrides**: Pass variables via JSON or key=value pairs

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `tf_directory` | Path to the Terraform configuration directory | No | `.` |
| `tfvars_files` | Comma-separated list of tfvars files | No | `""` |
| `backend_config_file` | Path to backend configuration file | No | `""` |
| `command` | Terraform command (`init`, `validate`, `plan`, `apply`, `destroy`) | Yes | `plan` |
| `workspace` | Terraform workspace to use | No | `default` |
| `azure_subscription_id` | Azure Subscription ID | No | `""` |
| `azure_tenant_id` | Azure Tenant ID | No | `""` |
| `azure_client_id` | Azure Client ID (optional; prefer OIDC) | No | `""` |
| `var_overrides` | JSON or key=value pairs for variable overrides | No | `""` |
| `log_level` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | `INFO` |

## Outputs

| Output | Description |
|--------|-------------|
| `plan_output` | Output from terraform plan command |
| `state_summary` | Summary of Terraform state changes |

## Usage

### Basic Example

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

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Run Terraform Plan
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform/examples/basic-usage
          command: plan
          tfvars_files: terraform.tfvars
```

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

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Run Terraform Apply
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform/examples/basic-usage
          command: apply
          tfvars_files: terraform.tfvars,production.tfvars
          workspace: production
          azure_subscription_id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          azure_tenant_id: ${{ secrets.AZURE_TENANT_ID }}
          azure_client_id: ${{ secrets.AZURE_CLIENT_ID }}
```

### Variable Overrides

```yaml
- name: Run Terraform with Variable Overrides
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    tf_directory: ./terraform
    command: plan
    var_overrides: |
      {"environment": "staging", "instance_count": "3"}
```

Or using key=value format:

```yaml
- name: Run Terraform with Variable Overrides
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    tf_directory: ./terraform
    command: plan
    var_overrides: |
      environment=staging
      instance_count=3
```

## Current Limitations

> **Note**: This action is under active development. The following features are planned but not yet fully implemented:

- **Azure OIDC Authentication**: Token exchange is stubbed; use `azure/login` action for now
- **Service Principal Authentication**: Partial implementation
- **Managed Identity Authentication**: Not yet implemented
- **Plan File Handling**: Plan files are not yet saved/retrieved between steps

See [docs/architecture.md](../../../docs/architecture.md) for the full roadmap.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=src

# Run linting
black --check src/
ruff check src/
```

### Local Development

```bash
# Set environment variables
export INPUT_TF_DIRECTORY="./terraform/examples/basic-usage"
export INPUT_COMMAND="plan"
export INPUT_LOG_LEVEL="DEBUG"

# Run the action locally
python -m src.main
```

## License

This project is licensed under the MIT License - see the [LICENSE](../../../LICENSE) file for details.
