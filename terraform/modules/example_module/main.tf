terraform {
  required_version = ">= 1.3.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0.0"
    }
  }
}

# Example AVM-style module: Azure Resource Group
# This serves as a placeholder to demonstrate module structure.
# Replace with actual Azure resources in production use.

resource "azurerm_resource_group" "this" {
  name     = var.name
  location = var.location
  tags     = var.tags
}
