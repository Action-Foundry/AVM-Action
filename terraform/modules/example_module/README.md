# Example Module

An example Azure Verified Module (AVM)-style module that creates an Azure Resource Group.

## Purpose

This module demonstrates the AVM conventions for Terraform modules:

- Standard variable naming (location, tags)
- Consistent output structure
- Documentation and formatting standards

## Usage

```hcl
module "resource_group" {
  source = "./modules/example_module"

  name     = "rg-example-dev"
  location = "eastus"

  tags = {
    Environment = "Development"
    Project     = "AVM-Action"
  }
}
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.3.0 |
| azurerm | >= 3.0.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| name | The name of the resource group | `string` | n/a | yes |
| location | The Azure region for the resource group | `string` | n/a | yes |
| tags | A map of tags to apply to the resource group | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| id | The ID of the resource group |
| name | The name of the resource group |
| location | The location of the resource group |
