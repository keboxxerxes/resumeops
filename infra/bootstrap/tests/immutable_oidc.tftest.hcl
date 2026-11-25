# Pure Terraform mocked plans: no AWS credentials, backend, apply or service API calls.
# All identities and the reserved .invalid recipient below are synthetic fixtures.
mock_provider "aws" {
  mock_resource "aws_iam_openid_connect_provider" {
    override_during = plan
    defaults = {
      arn = "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com"
    }
  }
  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "000000000000"
    }
  }
  mock_data "aws_partition" {
    defaults = {
      partition = "aws"
    }
  }
}

variables {
  name                       = "resumeops-synthetic-oidc"
  repository                 = "synthetic-owner/synthetic-repo"
  repository_owner_id        = "12345"
  repository_id              = "67890"
  alert_email                = "mock@example.invalid"
  existing_oidc_provider_arn = "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com"
}

run "exact_rendered_role_policies" {
  command = plan

  assert {
    condition = jsonencode({ for name, role in aws_iam_role.github : name => jsondecode(role.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"] }) == jsonencode({
      plan    = ["repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-plan", "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-drift"]
      apply   = ["repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-apply"]
      content = ["repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-content"]
    })
    error_message = "Rendered role subjects must exactly match the immutable three-role/four-environment mapping."
  }
  assert {
    condition     = alltrue([for role in values(aws_iam_role.github) : jsondecode(role.assume_role_policy).Version == "2012-10-17" && length(jsondecode(role.assume_role_policy).Statement) == 1 && jsondecode(role.assume_role_policy).Statement[0].Effect == "Allow" && jsondecode(role.assume_role_policy).Statement[0].Action == "sts:AssumeRoleWithWebIdentity" && jsonencode(jsondecode(role.assume_role_policy).Statement[0].Principal) == jsonencode({ Federated = "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com" }) && jsonencode(keys(jsondecode(role.assume_role_policy).Statement[0].Condition)) == jsonencode(["StringEquals"]) && jsonencode(keys(jsondecode(role.assume_role_policy).Statement[0].Condition.StringEquals)) == jsonencode(["token.actions.githubusercontent.com:aud", "token.actions.githubusercontent.com:sub"]) && jsondecode(role.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:aud"] == "sts.amazonaws.com"])
    error_message = "Rendered trust must have only the exact Allow/Federated/STS action and StringEquals audience/subject conditions."
  }
  assert {
    condition = jsonencode({ for name, role in aws_iam_role.github : name => jsondecode(role.assume_role_policy) }) == jsonencode({
      plan    = { Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Federated = "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com" }, Action = "sts:AssumeRoleWithWebIdentity", Condition = { StringEquals = { "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com", "token.actions.githubusercontent.com:sub" = ["repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-plan", "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-drift"] } } }] }
      apply   = { Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Federated = "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com" }, Action = "sts:AssumeRoleWithWebIdentity", Condition = { StringEquals = { "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com", "token.actions.githubusercontent.com:sub" = ["repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-apply"] } } }] }
      content = { Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Federated = "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com" }, Action = "sts:AssumeRoleWithWebIdentity", Condition = { StringEquals = { "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com", "token.actions.githubusercontent.com:sub" = ["repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-content"] } } }] }
    })
    error_message = "The complete rendered trust documents must have no extra keys, OR statements, NotAction/NotPrincipal or legacy acceptance."
  }
}

run "reject_adversarial_rendered_claims" {
  command = plan

  assert {
    condition = alltrue([for claim in [
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12346/synthetic-repo@67890:environment:production-plan" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67891:environment:production-plan" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:other-owner@12345/synthetic-repo@67890:environment:production-plan" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/other-repo@67890:environment:production-plan" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner/synthetic-repo:environment:production-plan" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner/synthetic-repo@67890:environment:production-plan" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo:environment:production-plan" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:ref:refs/heads/main" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:pull_request" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-other" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:*" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-apply" },
      { role = "plan", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-content" },
      { role = "plan", audience = "https://github.com/synthetic-owner", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-plan" },
      { role = "plan", audience = "", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-plan" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12346/synthetic-repo@67890:environment:production-apply" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67891:environment:production-apply" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:other-owner@12345/synthetic-repo@67890:environment:production-apply" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/other-repo@67890:environment:production-apply" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner/synthetic-repo:environment:production-apply" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner/synthetic-repo@67890:environment:production-apply" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo:environment:production-apply" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:ref:refs/heads/main" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:pull_request" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-other" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:*" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-plan" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-content" },
      { role = "apply", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-drift" },
      { role = "apply", audience = "https://github.com/synthetic-owner", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-apply" },
      { role = "apply", audience = "", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-apply" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12346/synthetic-repo@67890:environment:production-content" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67891:environment:production-content" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:other-owner@12345/synthetic-repo@67890:environment:production-content" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/other-repo@67890:environment:production-content" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner/synthetic-repo:environment:production-content" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner/synthetic-repo@67890:environment:production-content" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo:environment:production-content" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:ref:refs/heads/main" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:pull_request" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-other" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:*" },
      { role = "content", audience = "sts.amazonaws.com", subject = "" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-plan" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-apply" },
      { role = "content", audience = "sts.amazonaws.com", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-drift" },
      { role = "content", audience = "https://github.com/synthetic-owner", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-content" },
      { role = "content", audience = "", subject = "repo:synthetic-owner@12345/synthetic-repo@67890:environment:production-content" },
    ] : !(jsondecode(aws_iam_role.github[claim.role].assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:aud"] == claim.audience && contains(jsondecode(aws_iam_role.github[claim.role].assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"], claim.subject))])
    error_message = "Rendered StringEquals trust must reject wrong identities, legacy/name-only subjects, cross-role environments and wrong audiences."
  }
}

run "owner_id_changes_subject" {
  command = plan

  variables {
    repository_owner_id = "54321"
  }

  assert {
    condition     = alltrue(flatten([for role in values(aws_iam_role.github) : [for subject in jsondecode(role.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"] : startswith(subject, "repo:synthetic-owner@54321/synthetic-repo@67890:environment:")]]))
    error_message = "Every rendered role must use the exact supplied canonical ID strings without arithmetic or fallback."
  }
}

run "repository_id_changes_subject" {
  command = plan

  variables {
    repository_id = "98765"
  }

  assert {
    condition     = alltrue(flatten([for role in values(aws_iam_role.github) : [for subject in jsondecode(role.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"] : startswith(subject, "repo:synthetic-owner@12345/synthetic-repo@98765:environment:")]]))
    error_message = "Every rendered role must use the exact supplied canonical ID strings without arithmetic or fallback."
  }
}

run "terraform_numeric_string_coercion" {
  command = plan

  variables {
    repository_owner_id = 1
    repository_id       = 2
  }

  assert {
    condition     = alltrue(flatten([for role in values(aws_iam_role.github) : [for subject in jsondecode(role.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"] : startswith(subject, "repo:synthetic-owner@1/synthetic-repo@2:environment:")]]))
    error_message = "Every rendered role must use the exact supplied canonical ID strings without arithmetic or fallback."
  }
}

run "large_opaque_string_ids" {
  command = plan

  variables {
    repository_owner_id = "123456789012345678901234567890"
    repository_id       = "987654321098765432109876543210"
  }

  assert {
    condition     = alltrue(flatten([for role in values(aws_iam_role.github) : [for subject in jsondecode(role.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"] : startswith(subject, "repo:synthetic-owner@123456789012345678901234567890/synthetic-repo@987654321098765432109876543210:environment:")]]))
    error_message = "Every rendered role must use the exact supplied canonical ID strings without arithmetic or fallback."
  }
}

run "managed_provider_immutable_trust" {
  command = plan

  variables {
    existing_oidc_provider_arn = null
  }

  assert {
    condition     = length(aws_iam_openid_connect_provider.github) == 1 && aws_iam_openid_connect_provider.github[0].url == "https://token.actions.githubusercontent.com" && toset(aws_iam_openid_connect_provider.github[0].client_id_list) == toset(["sts.amazonaws.com"]) && alltrue([for role in values(aws_iam_role.github) : jsondecode(role.assume_role_policy).Statement[0].Principal.Federated == "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com"])
    error_message = "All rendered role principals must bind the exact mocked managed GitHub issuer with the STS audience."
  }
}

run "repository_owner_id_invalid_0" {
  command = plan

  variables {
    repository_owner_id = ""
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_1" {
  command = plan

  variables {
    repository_owner_id = "0"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_2" {
  command = plan

  variables {
    repository_owner_id = "01"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_3" {
  command = plan

  variables {
    repository_owner_id = "-1"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_4" {
  command = plan

  variables {
    repository_owner_id = "+1"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_5" {
  command = plan

  variables {
    repository_owner_id = " 1"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_6" {
  command = plan

  variables {
    repository_owner_id = "1 "
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_7" {
  command = plan

  variables {
    repository_owner_id = "1.0"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_8" {
  command = plan

  variables {
    repository_owner_id = "1e3"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_9" {
  command = plan

  variables {
    repository_owner_id = "*"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_10" {
  command = plan

  variables {
    repository_owner_id = "1x"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_owner_id_invalid_11" {
  command = plan

  variables {
    repository_owner_id = "\n1"
  }

  expect_failures = [var.repository_owner_id]

}

run "repository_id_invalid_0" {
  command = plan

  variables {
    repository_id = ""
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_1" {
  command = plan

  variables {
    repository_id = "0"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_2" {
  command = plan

  variables {
    repository_id = "01"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_3" {
  command = plan

  variables {
    repository_id = "-1"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_4" {
  command = plan

  variables {
    repository_id = "+1"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_5" {
  command = plan

  variables {
    repository_id = " 1"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_6" {
  command = plan

  variables {
    repository_id = "1 "
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_7" {
  command = plan

  variables {
    repository_id = "1.0"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_8" {
  command = plan

  variables {
    repository_id = "1e3"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_9" {
  command = plan

  variables {
    repository_id = "*"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_10" {
  command = plan

  variables {
    repository_id = "1x"
  }

  expect_failures = [var.repository_id]

}

run "repository_id_invalid_11" {
  command = plan

  variables {
    repository_id = "\n1"
  }

  expect_failures = [var.repository_id]

}
