name       = "resumeops-replace-unique"
repository = "REPLACE/REPLACE"
region     = "us-east-1"
# alert_email must come from private TF_VAR_alert_email, never a committed file.
# existing_oidc_provider_arn: set privately if GitHub OIDC provider already exists.
# content_distribution_id: set privately after first site deployment.
