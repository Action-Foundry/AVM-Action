# Terraform Directory

This directory contains Terraform modules and examples for use with the `avm-action` GitHub Action.

## Structure

```
terraform/
├── modules/          # Reusable Terraform modules
│   └── example_module/   # Example AVM-style module
└── examples/         # Example stacks/configurations
    └── basic-usage/      # Basic usage example
```

## Modules

The `modules/` directory contains reusable Terraform modules following [Azure Verified Modules (AVM)](https://azure.github.io/Azure-Verified-Modules/) patterns and conventions.

### Module Conventions

- **Naming**: Use lowercase with underscores (e.g., `resource_group`, `storage_account`)
- **Standard Variables**: All modules should accept `location`, `resource_group_name`, and `tags`
- **Outputs**: Provide meaningful outputs for resource IDs and properties
- **Documentation**: Each module should have a README.md explaining usage

## Examples

The `examples/` directory contains complete stack configurations that demonstrate how to use modules with `avm-action`.

### Running Examples Locally

```bash
cd examples/basic-usage
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### Using Examples with AVM Action

Examples are designed to work seamlessly with the `avm-action` GitHub Action:

```yaml
- name: Run Terraform Plan
  uses: Action-Foundry/AVM-Action/.github/actions/avm-action@main
  with:
    tf_directory: ./terraform/examples/basic-usage
    command: plan
    tfvars_files: terraform.tfvars
```

## Relationship with AVM Action

The `avm-action` consumes Terraform configurations from this directory structure:

1. **Directory**: Set via `tf_directory` input
2. **Variables**: Pass tfvars files via `tfvars_files` input
3. **Workspace**: Select workspace via `workspace` input
4. **Backend**: Configure backend via `backend_config_file` input

See [docs/terraform-usage.md](../docs/terraform-usage.md) for detailed guidance on structuring Terraform code for use with `avm-action`.
