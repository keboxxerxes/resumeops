locals {
  state_arn = "${aws_s3_bucket.state.arn}/${local.state_key}"
  lock_arn  = "${aws_s3_bucket.state.arn}/${local.state_key}.tflock"
  site_arn  = "arn:${local.partition}:s3:::${local.site_bucket}"
  state_statements = [
    {
      Effect = "Allow", Action = ["s3:ListBucket"], Resource = [aws_s3_bucket.state.arn], Condition = {
        StringEquals = {
          "s3:prefix" = [local.state_key, "${local.state_key}.tflock"]
        }
      }
    },
    {
      Effect = "Allow", Action = ["s3:GetObject"], Resource = [local.state_arn]
    },
    {
      Effect = "Allow", Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"], Resource = [local.lock_arn]
    }
  ]
  read_statements = [
    {
      Effect = "Allow", Action = ["s3:GetBucketAcl", "s3:GetBucketCORS", "s3:GetBucketWebsite", "s3:GetBucketLogging", "s3:GetAccelerateConfiguration", "s3:GetBucketRequestPayment", "s3:GetReplicationConfiguration", "s3:GetBucketObjectLockConfiguration", "s3:GetBucketPolicy", "s3:GetBucketPublicAccessBlock", "s3:GetBucketOwnershipControls", "s3:GetEncryptionConfiguration", "s3:GetBucketVersioning", "s3:GetLifecycleConfiguration", "s3:GetBucketLocation", "s3:GetBucketTagging", "s3:ListBucket"], Resource = [local.site_arn]
    },
    {
      Effect = "Allow", Action = ["cloudfront:GetDistribution", "cloudfront:GetDistributionConfig", "cloudfront:GetOriginAccessControl", "cloudfront:GetResponseHeadersPolicy", "cloudfront:ListTagsForResource"], Resource = ["${local.cf_prefix}:distribution/${coalesce(var.content_distribution_id, "NOTCONFIGURED")}", "${local.cf_prefix}:origin-access-control/${coalesce(var.origin_access_control_id, "NOTCONFIGURED")}", "${local.cf_prefix}:response-headers-policy/${coalesce(var.response_headers_policy_id, "NOTCONFIGURED")}"]
    }
  ]
}
resource "aws_iam_role_policy" "plan" {
  role = aws_iam_role.github["plan"].id
  policy = jsonencode({
    Version = "2012-10-17", Statement = concat(local.state_statements, local.read_statements)
  })
}
resource "aws_iam_role_policy" "apply" {
  role = aws_iam_role.github["apply"].id
  policy = jsonencode({
    Version = "2012-10-17", Statement = concat(local.state_statements, local.read_statements, [
      {
        Effect = "Allow", Action = ["s3:PutObject"], Resource = [local.state_arn]
      },
      {
        Effect = "Allow", Action = ["s3:CreateBucket", "s3:DeleteBucket", "s3:PutBucketPolicy", "s3:DeleteBucketPolicy", "s3:PutBucketPublicAccessBlock", "s3:PutBucketOwnershipControls", "s3:PutEncryptionConfiguration", "s3:PutBucketVersioning", "s3:PutLifecycleConfiguration", "s3:PutBucketTagging"], Resource = [local.site_arn]
      },
      {
        Effect = "Allow", Action = ["cloudfront:UpdateDistribution", "cloudfront:DeleteDistribution", "cloudfront:TagResource", "cloudfront:UntagResource"], Resource = ["${local.cf_prefix}:distribution/${coalesce(var.content_distribution_id, "NOTCONFIGURED")}"], Condition = {
          StringEquals = {
            "aws:ResourceTag/Project" = "ResumeOps"
          }
        }
      },
      {
        Effect = "Allow", Action = ["cloudfront:UpdateOriginAccessControl", "cloudfront:DeleteOriginAccessControl", "cloudfront:UpdateResponseHeadersPolicy", "cloudfront:DeleteResponseHeadersPolicy"], Resource = ["${local.cf_prefix}:origin-access-control/${coalesce(var.origin_access_control_id, "NOTCONFIGURED")}", "${local.cf_prefix}:response-headers-policy/${coalesce(var.response_headers_policy_id, "NOTCONFIGURED")}"]
      }
    ])
  })
}
variable "content_distribution_id" {
  type        = string
  default     = null
  description = "Set to exact created distribution ID after first site apply, then operator reapplies bootstrap to enable content deploy."
  validation {
    condition     = var.content_distribution_id == null || can(regex("^[A-Z0-9]+$", var.content_distribution_id))
    error_message = "Use an exact distribution ID."

  }
}
resource "aws_iam_role_policy" "content" {
  role = aws_iam_role.github["content"].id
  policy = jsonencode({
    Version = "2012-10-17", Statement = concat([
      {
        Effect = "Allow", Action = ["s3:PutObject"], Resource = [for path in ["index.html", "styles.css", "app.js", "deployment.json"] : "${local.site_arn}/${path}"]
      }
      ], var.content_distribution_id == null ? [] : [
      {
        Effect = "Allow", Action = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"], Resource = ["${local.cf_prefix}:distribution/${var.content_distribution_id}"]
      }
    ])
  })
}


