name                = "resumeops-replace-unique"
repository          = "REPLACE/REPLACE"
repository_owner_id = "REPLACE_WITH_GITHUB_OWNER_ID"
repository_id       = "REPLACE_WITH_GITHUB_REPOSITORY_ID"
region              = "us-east-1"
# alert_email must come from private TF_VAR_alert_email, never a committed file.
# existing_oidc_provider_arn: set privately if GitHub OIDC provider already exists.
# content_distribution_id: set privately after first site deployment.
# GitHub IDs are required opaque decimal strings; obtain both from verified repository metadata.
