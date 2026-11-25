resource "aws_s3_bucket" "site" {
  #checkov:skip=CKV_AWS_18:No S3 access audit log selected for this public static site; log delivery is free but storage/access fees and visitor-data retention remain. Origin blocks prevent bypass but do not provide auditing.
  #checkov:skip=CKV_AWS_144:Single region required; versioned bucket provides recovery without replication cost.
  #checkov:skip=CKV_AWS_145:SSE-S3 provides at-rest encryption without separate key-policy separation. Customer-managed KMS key monthly/request costs excluded; AWS-managed KMS has no key storage charge but request charges may apply.
  #checkov:skip=CKV2_AWS_62:No event consumer or event-alert requirement in scope; absent notifications mean no event-driven object-change monitoring.

  bucket        = var.name
  force_destroy = false
}
resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = aws_s3_bucket.site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_ownership_controls" "site" {
  bucket = aws_s3_bucket.site.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "site" {
  bucket = aws_s3_bucket.site.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

  }
}
resource "aws_s3_bucket_versioning" "site" {
  bucket = aws_s3_bucket.site.id
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_lifecycle_configuration" "site" {
  bucket = aws_s3_bucket.site.id
  rule {
    id     = "bounded-history"
    status = "Enabled"
    filter {
      prefix = ""
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }

  }
  depends_on = [aws_s3_bucket_versioning.site]
}
resource "aws_cloudfront_origin_access_control" "site" {
  name                              = var.name
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
resource "aws_cloudfront_response_headers_policy" "site" {
  name = var.name
  security_headers_config {
    content_type_options {
      override = true
    }
    frame_options {
      frame_option = "DENY"
      override     = true

    }
    referrer_policy {
      referrer_policy = "no-referrer"
      override        = true

    }
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = true
      override                   = true

    }
    content_security_policy {
      content_security_policy = "default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; upgrade-insecure-requests"
      override                = true

    }

  }
}
resource "aws_cloudfront_distribution" "site" {
  #checkov:skip=CKV_AWS_86:No visitor request/audit logs; request analysis is unavailable. Data minimization and cost choice; HTTPS smoke verifies sampled delivery only and does not replace logging.
  #checkov:skip=CKV_AWS_310:Single private S3 origin is intentional; no second persistent environment or failover origin.
  #checkov:skip=CKV_AWS_374:Public professional portfolio intentionally reachable globally.
  #checkov:skip=CKV_AWS_174:AWS default CloudFront certificate fixes minimum viewer TLS policy; custom domain/certificate excluded. HTTPS remains mandatory; legacy client TLS residual documented.
  #checkov:skip=CKV_AWS_68:Read-only static assets/no backend; pay-as-you-go WAF exceeds target cost. Free CloudFront flat-rate WAF is a separate unenrolled offering, not this distribution.
  #checkov:skip=CKV2_AWS_42:Specification requires default CloudFront hostname; no custom certificate/domain.
  #checkov:skip=CKV2_AWS_47:No runtime or Log4j; no WAF inspection/managed rules. Pay-as-you-go WAF cost excluded; separate free flat-rate plan not enrolled. CSP/origin isolation address different risks.

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  wait_for_deployment = true
  origin {
    domain_name              = aws_s3_bucket.site.bucket_regional_domain_name
    origin_id                = "private-s3"
    origin_access_control_id = aws_cloudfront_origin_access_control.site.id

  }
  default_cache_behavior {
    target_origin_id           = "private-s3"
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods            = ["GET", "HEAD"]
    cached_methods             = ["GET", "HEAD"]
    compress                   = true
    cache_policy_id            = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    response_headers_policy_id = aws_cloudfront_response_headers_policy.site.id

  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
data "aws_iam_policy_document" "site" {
  statement {
    sid       = "CloudFrontOnly"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.site.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]

    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.site.arn]

    }

  }
  statement {
    sid       = "DenyInsecureTransport"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.site.arn, "${aws_s3_bucket.site.arn}/*"]
    principals {
      type        = "*"
      identifiers = ["*"]

    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]

    }

  }
}
resource "aws_s3_bucket_policy" "site" {
  bucket     = aws_s3_bucket.site.id
  policy     = data.aws_iam_policy_document.site.json
  depends_on = [aws_s3_bucket_public_access_block.site]
}

