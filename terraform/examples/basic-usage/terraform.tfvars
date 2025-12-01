# Example tfvars file for basic-usage example
# This file demonstrates how to pass variables to Terraform via avm-action

resource_group_name = "rg-avm-action-example"
location            = "eastus"
environment         = "dev"

tags = {
  Owner      = "DevOps"
  CostCenter = "Engineering"
}
