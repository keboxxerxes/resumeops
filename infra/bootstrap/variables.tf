variable "region" {
  type    = string
  default = "us-east-1"
}
variable "name" {
  type = string
  validation {
    condition     = can(regex("^resumeops-[a-z0-9-]+$", var.name))
    error_message = "Use a resumeops- prefixed unique name."

  }
}
variable "repository" {
  type = string
  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.repository))
    error_message = "Provide the exact owner/repository, with no wildcards."

  }
}
variable "alert_email" {
  type      = string
  sensitive = true
  validation {
    condition     = can(regex("^[^@ ]+@[^@ ]+\\.[^@ ]+$", var.alert_email))
    error_message = "Provide a private operator email through TF_VAR_alert_email."

  }
}
variable "existing_oidc_provider_arn" {
  type        = string
  default     = null
  description = "Use an existing GitHub provider if the account already has one; do not create duplicates."
}

variable "origin_access_control_id" {
  type    = string
  default = null
  validation {
    condition     = var.origin_access_control_id == null || can(regex("^[A-Z0-9]+$", var.origin_access_control_id))
    error_message = "Use exact OAC ID after initial site apply."
  }
}
variable "response_headers_policy_id" {
  type    = string
  default = null
  validation {
    condition     = var.response_headers_policy_id == null || can(regex("^[a-f0-9-]+$", var.response_headers_policy_id))
    error_message = "Use exact response headers policy ID after initial site apply."
  }
}
