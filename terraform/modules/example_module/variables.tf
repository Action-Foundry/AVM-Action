variable "name" {
  description = "The name of the resource group"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9-_]{1,90}$", var.name))
    error_message = "Resource group name must be 1-90 characters and can only contain alphanumeric, hyphens, and underscores."
  }
}

variable "location" {
  description = "The Azure region for the resource group"
  type        = string
}

variable "tags" {
  description = "A map of tags to apply to the resource group"
  type        = map(string)
  default     = {}
}
