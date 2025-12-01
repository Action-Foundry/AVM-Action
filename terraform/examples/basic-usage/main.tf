terraform {
  required_version = ">= 1.3.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0.0"
    }
  }

  # Backend configuration placeholder
  # Uncomment and configure for remote state storage
  # backend "azurerm" {
  #   resource_group_name  = "rg-terraform-state"
  #   storage_account_name = "stterraformstate"
  #   container_name       = "tfstate"
  #   key                  = "basic-usage.tfstate"
  # }
}

provider "azurerm" {
  features {}
}

# Use the example module to create a resource group
module "resource_group" {
  source = "../../modules/example_module"

  name     = var.resource_group_name
  location = var.location

  tags = merge(
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = "AVM-Action-Example"
    },
    var.tags
  )
}
