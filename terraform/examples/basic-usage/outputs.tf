output "resource_group_id" {
  description = "The ID of the created resource group"
  value       = module.resource_group.id
}

output "resource_group_name" {
  description = "The name of the created resource group"
  value       = module.resource_group.name
}

output "resource_group_location" {
  description = "The location of the created resource group"
  value       = module.resource_group.location
}
