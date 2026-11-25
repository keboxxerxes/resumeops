provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project = "ResumeOps", Environment = "bootstrap"
    }
  }
}
data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
locals {
  partition    = data.aws_partition.current.partition
  account      = data.aws_caller_identity.current.account_id
  state_bucket = "${var.name}-state"
  site_bucket  = "${var.name}-production"
  state_key    = "site/production/terraform.tfstate"
  cf_prefix    = "arn:${local.partition}:cloudfront::${local.account}"
  provider_arn = var.existing_oidc_provider_arn != null ? var.existing_oidc_provider_arn : aws_iam_openid_connect_provider.github[0].arn
}
resource "aws_s3_bucket" "state" {
  #checkov:skip=CKV_AWS_18:State data-access audit logging is absent. S3 log delivery is free; storage/access costs and additional audit infrastructure omitted. Exact IAM/versioning/locks prevent other risks but do not audit state reads.
  #checkov:skip=CKV_AWS_144:Single-region versioned state is not regional disaster recovery. A private operator recovery backup is a release prerequisite, not verified to exist.
  #checkov:skip=CKV_AWS_145:SSE-S3 at rest; no independent KMS key-policy boundary. Customer-managed key monthly/request costs excluded; AWS-managed KMS storage itself is free, requests may cost.
  #checkov:skip=CKV2_AWS_62:No event-consumer requirement; no event-driven state-change alerting. Native locks control concurrency and are not event monitoring.

  bucket        = local.state_bucket
  force_destroy = false
  lifecycle {
    prevent_destroy = true
  }
}
resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_ownership_controls" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_lifecycle_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    id     = "bounded-history"
    status = "Enabled"
    filter {
      prefix = ""
    }
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }

  }
  depends_on = [aws_s3_bucket_versioning.state]
}
resource "aws_s3_bucket_policy" "state" {
  bucket = aws_s3_bucket.state.id
  policy = jsonencode({
    Version = "2012-10-17", Statement = [{
      Sid = "DenyInsecureTransport", Effect = "Deny", Principal = "*", Action = "s3:*", Resource = [aws_s3_bucket.state.arn, "${aws_s3_bucket.state.arn}/*"], Condition = {
        Bool = {
          "aws:SecureTransport" = "false"
        }
      }
    }]
  })
}
resource "aws_iam_openid_connect_provider" "github" {
  count          = var.existing_oidc_provider_arn == null ? 1 : 0
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}
locals {
  repository_owner = split("/", var.repository)[0]
  repository_name  = split("/", var.repository)[1]
  oidc_repository  = "${local.repository_owner}@${var.repository_owner_id}/${local.repository_name}@${var.repository_id}"
}
locals {
  subjects = {
    plan    = ["production-plan", "production-drift"]
    apply   = ["production-apply"]
    content = ["production-content"]

  }
}
resource "aws_iam_role" "github" {
  for_each             = local.subjects
  name                 = "${var.name}-${each.key}"
  max_session_duration = 3600
  assume_role_policy = jsonencode({
    Version = "2012-10-17", Statement = [{
      Effect = "Allow", Principal = {
        Federated = local.provider_arn
        }, Action = "sts:AssumeRoleWithWebIdentity", Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com", "token.actions.githubusercontent.com:sub" = [for env in each.value : "repo:${local.oidc_repository}:environment:${env}"]
        }
      }
    }]
  })
}
resource "aws_budgets_budget" "monthly" {
  name         = "${var.name}-monthly"
  budget_type  = "COST"
  limit_amount = "5"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  dynamic "notification" {
    for_each = [1, 3, 5]
    content {
      comparison_operator        = "GREATER_THAN"
      notification_type          = "ACTUAL"
      threshold                  = notification.value
      threshold_type             = "ABSOLUTE_VALUE"
      subscriber_email_addresses = [var.alert_email]

    }

  }
}

