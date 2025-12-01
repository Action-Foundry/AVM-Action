# Basic Usage Example

This example demonstrates a simple Terraform configuration using the example module and `avm-action`.

## Overview

This stack creates a basic Azure Resource Group using the `example_module`. It showcases:

- How to structure tfvars files
- Module usage patterns
- Integration with `avm-action`

## Prerequisites

- Azure subscription
- Azure CLI authenticated (`az login`)
- Terraform >= 1.3.0

## Running Locally

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan -var-file=terraform.tfvars

# Apply changes
terraform apply -var-file=terraform.tfvars

# Destroy resources
terraform destroy -var-file=terraform.tfvars
```

## Using with AVM Action

This example is designed to be used with the `avm-action` GitHub Action:

```yaml
name: Deploy Basic Example

on:
  push:
    branches: [main]
    paths:
      - 'terraform/examples/basic-usage/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Terraform Plan
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform/examples/basic-usage
          command: plan
          tfvars_files: terraform.tfvars

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ./terraform/examples/basic-usage
          command: apply
          tfvars_files: terraform.tfvars
```

## Variables

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `resource_group_name` | Name for the resource group | `string` | Yes |
| `location` | Azure region | `string` | Yes |
| `environment` | Environment name | `string` | No |
| `tags` | Additional tags | `map(string)` | No |
