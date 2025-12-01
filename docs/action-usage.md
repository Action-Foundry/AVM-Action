# Action Usage Guide

This guide explains how to use the `avm-action` GitHub Action in your workflows.

> **Note**: The action uses a Docker container with Terraform pre-installed. You don't need to use `hashicorp/setup-terraform` separately.

## Basic Usage

### Minimal Configuration

```yaml
- name: Run Terraform Plan
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    command: plan
```

### Full Configuration

```yaml
- name: Run Terraform Apply
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    tf_directory: ./terraform/environments/production
    tfvars_files: production.tfvars,common.tfvars
    backend_config_file: backend.hcl
    command: apply
    workspace: production
    azure_subscription_id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    azure_tenant_id: ${{ secrets.AZURE_TENANT_ID }}
    azure_client_id: ${{ secrets.AZURE_CLIENT_ID }}
    var_overrides: '{"environment": "prod"}'
    log_level: INFO
```

## Typical Pipeline Patterns

### Validate → Plan → Apply

This is the most common pattern for infrastructure changes:

```yaml
name: Terraform Deployment

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Terraform Validate
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform
          command: validate

  plan:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Terraform Plan
        id: plan
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform
          command: plan
          tfvars_files: terraform.tfvars

      # TODO: Add plan output to PR comment when implemented

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
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
          tfvars_files: terraform.tfvars
```

### Multi-Environment Deployment

```yaml
name: Multi-Environment Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - dev
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
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
          tfvars_files: ${{ github.event.inputs.environment }}.tfvars,common.tfvars
          workspace: ${{ github.event.inputs.environment }}
```

## Directory Layout

The action expects your Terraform configuration to follow a standard layout:

```
terraform/
├── main.tf              # Main configuration
├── variables.tf         # Variable definitions
├── outputs.tf           # Output definitions
├── providers.tf         # Provider configuration
├── backend.hcl          # Backend configuration (optional)
├── terraform.tfvars     # Default variables
├── dev.tfvars           # Development variables
├── staging.tfvars       # Staging variables
└── production.tfvars    # Production variables
```

## Input Reference

| Input | Description | Default |
|-------|-------------|---------|
| `tf_directory` | Path to Terraform configuration | `.` |
| `tfvars_files` | Comma-separated tfvars files | `""` |
| `backend_config_file` | Path to backend config | `""` |
| `command` | Terraform command to run | `plan` |
| `workspace` | Workspace to use | `default` |
| `azure_subscription_id` | Azure Subscription ID | `""` |
| `azure_tenant_id` | Azure Tenant ID | `""` |
| `azure_client_id` | Azure Client ID | `""` |
| `var_overrides` | JSON or key=value overrides | `""` |
| `log_level` | Logging level | `INFO` |

## Output Reference

| Output | Description |
|--------|-------------|
| `plan_output` | Output from terraform plan |
| `state_summary` | Summary of state changes |

## Error Handling

The action exits with non-zero status codes for:

- Invalid configuration
- Terraform command failures
- Authentication failures

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid command` | Unknown Terraform command | Use: init, validate, plan, apply, destroy |
| `tf_directory cannot be empty` | Empty directory path | Provide a valid path |
| `Terraform not found` | Missing Terraform binary | Add setup-terraform step |

## Debugging

Enable debug logging for troubleshooting:

```yaml
- name: Terraform Plan (Debug)
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    tf_directory: ./terraform
    command: plan
    log_level: DEBUG
```

## Best Practices

1. **Always validate first**: Run `validate` before `plan`
2. **Use workspaces**: Separate environments with workspaces
3. **Protect production**: Use GitHub Environments with approvals
4. **Use OIDC**: Prefer OIDC over service principal secrets
5. **Pin versions**: Pin action version to a specific tag or SHA
