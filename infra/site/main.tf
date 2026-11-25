provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project = "ResumeOps", Environment = "production"
    }
  }
}
variable "region" {
  type    = string
  default = "us-east-1"
}
variable "site_bucket" {
  type = string
  validation {
    condition     = can(regex("^resumeops-[a-z0-9-]+-production$", var.site_bucket))
    error_message = "Use a unique resumeops-<suffix>-production bucket name."

  }
}
module "website" {
  source = "../modules/website"
  name   = var.site_bucket
}
output "bucket_name" {
  value     = module.website.bucket_name
  sensitive = true
}
output "distribution_id" {
  value     = module.website.distribution_id
  sensitive = true
}
output "domain_name" {
  value     = module.website.domain_name
  sensitive = true
}

