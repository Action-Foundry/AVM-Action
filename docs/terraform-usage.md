# Terraform Usage Guide

This guide explains how to structure your Terraform code for use with the `avm-action` GitHub Action.

## Overview

The `avm-action` is designed to work with Terraform configurations following Azure Verified Modules (AVM) patterns. This guide covers best practices for organizing your infrastructure code.

## Directory Structure

### Recommended Layout

```
terraform/
├── modules/                    # Reusable modules
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   └── compute/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
├── environments/               # Environment-specific configurations
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.hcl
│   ├── staging/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.hcl
│   └── production/
│       ├── main.tf
│       ├── terraform.tfvars
│       └── backend.hcl
└── shared/                     # Shared configurations
    └── common.tfvars
```

### Alternative: Single Directory with Workspaces

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── backend.hcl
├── common.tfvars
├── dev.tfvars
├── staging.tfvars
└── production.tfvars
```

## Azure Verified Modules (AVM) Patterns

### Module Conventions

AVM modules follow specific conventions for consistency:

```hcl
# modules/resource_group/main.tf

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0.0"
    }
  }
}

resource "azurerm_resource_group" "this" {
  name     = var.name
  location = var.location
  tags     = var.tags
}
```

### Standard Variables

All modules should accept these standard variables:

```hcl
# modules/resource_group/variables.tf

variable "name" {
  description = "The name of the resource"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9-_]{1,90}$", var.name))
    error_message = "Name must be 1-90 alphanumeric characters."
  }
}

variable "location" {
  description = "Azure region for the resource"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the resource"
  type        = map(string)
  default     = {}
}
```

### Standard Outputs

```hcl
# modules/resource_group/outputs.tf

output "id" {
  description = "The resource ID"
  value       = azurerm_resource_group.this.id
}

output "name" {
  description = "The resource name"
  value       = azurerm_resource_group.this.name
}
```

## Using AVM Modules from Registry

Azure Verified Modules are available from the Terraform Registry:

```hcl
module "resource_group" {
  source  = "Azure/avm-res-resources-resourcegroup/azurerm"
  version = "0.1.0"

  name     = "rg-myapp-dev"
  location = "eastus"
  tags     = local.common_tags
}

module "virtual_network" {
  source  = "Azure/avm-res-network-virtualnetwork/azurerm"
  version = "0.2.0"

  resource_group_name = module.resource_group.name
  name                = "vnet-myapp-dev"
  location            = "eastus"
  address_space       = ["10.0.0.0/16"]

  subnets = {
    subnet1 = {
      address_prefixes = ["10.0.1.0/24"]
    }
  }
}
```

## Variable Files (tfvars)

### Structure

Organize variables by scope:

```hcl
# common.tfvars - Shared across all environments
project_name = "myapp"
owner        = "platform-team"

# dev.tfvars - Development-specific
environment    = "dev"
instance_count = 1
sku            = "Basic"

# production.tfvars - Production-specific
environment    = "production"
instance_count = 3
sku            = "Premium"
```

### Using with avm-action

```yaml
- name: Terraform Plan (Dev)
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    tf_directory: ./terraform
    command: plan
    tfvars_files: common.tfvars,dev.tfvars
    workspace: dev
```

## Backend Configuration

### Azure Storage Backend

```hcl
# backend.hcl
resource_group_name  = "rg-terraform-state"
storage_account_name = "stterraformstate"
container_name       = "tfstate"
key                  = "myapp/terraform.tfstate"
```

```hcl
# main.tf
terraform {
  backend "azurerm" {}
}
```

### Using with avm-action

```yaml
- name: Terraform Init
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    tf_directory: ./terraform
    command: init
    backend_config_file: backend.hcl
```

## Workspace Strategy

### When to Use Workspaces

Workspaces are useful for:
- Same configuration, different environments
- Ephemeral environments (PR-based)
- Cost separation

### Workspace Naming Convention

```
{environment}-{region}
```

Examples: `dev-eastus`, `staging-westeurope`, `production-eastus`

### Workspace-aware Configuration

```hcl
locals {
  environment = terraform.workspace
  
  instance_count = {
    dev        = 1
    staging    = 2
    production = 3
  }
}

resource "azurerm_virtual_machine" "main" {
  count = local.instance_count[local.environment]
  # ...
}
```

## Integration with avm-action

### Complete Example

```yaml
name: Infrastructure Deployment

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'
  pull_request:
    branches: [main]
    paths:
      - 'terraform/**'

env:
  TF_DIRECTORY: ./terraform/environments/production
  WORKSPACE: production

jobs:
  terraform:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Terraform Init
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ${{ env.TF_DIRECTORY }}
          command: init
          backend_config_file: backend.hcl

      - name: Terraform Plan
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ${{ env.TF_DIRECTORY }}
          command: plan
          tfvars_files: terraform.tfvars,../../shared/common.tfvars
          workspace: ${{ env.WORKSPACE }}

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
        with:
          tf_directory: ${{ env.TF_DIRECTORY }}
          command: apply
          tfvars_files: terraform.tfvars,../../shared/common.tfvars
          workspace: ${{ env.WORKSPACE }}
```

## Best Practices

### General
1. **Pin provider versions** - Avoid unexpected breaking changes
2. **Use modules** - Don't repeat yourself
3. **Validate early** - Run `terraform validate` in CI
4. **Format consistently** - Use `terraform fmt`

### For AVM
1. **Follow naming conventions** - Use standard prefixes (rg-, vnet-, etc.)
2. **Tag everything** - Include Owner, Environment, CostCenter
3. **Use data sources** - Reference existing resources safely
4. **Document modules** - Every module needs a README

### Security
1. **Never commit secrets** - Use GitHub Secrets
2. **Prefer OIDC** - Avoid long-lived credentials
3. **Lock state files** - Enable state locking
4. **Review plans** - Always review before apply

## Resources

- [Azure Verified Modules](https://azure.github.io/Azure-Verified-Modules/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Azure Naming Convention](https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/naming-and-tagging)
