# Local provider mTLS diagnosis

Date: 2026-11-25. Local-only diagnostics; no AWS API, provider configuration, role assumption, resource creation, IAM change, publication or destruction. Credentials were neither inspected nor exercised. Raw TLS certificates, ephemeral private keys, handshake records and debug logs are ignored under `.tools/`; none are included here.

## Observations

| Experiment | Actual result |
|---|---|
| Pinned Terraform 1.17.2, AWS provider 6.74.0, both project roots | Provider schema retrieval fails before validation completes. Independent command evidence is in the orchestrator/reviewer reports. |
| Terraform 1.17.2 core-only/built-in control | Orchestrator ran init and validate successfully, both exit 0. This tests the evaluator without the external AWS plugin, not AWS provider schema validity. |
| Human-authorized native outside-sandbox comparison | Both project-root init commands exit 0; both validate commands exit 1 before successful schema validation. The requested execution boundary comparison did not resolve or attribute the interception. |
| Existing Ubuntu WSL alternative | Availability query exits 0. Exact-pin Linux downloads/checksums verified, but launch exits 1 with `Wsl/Service/WSAETIMEDOUT` before Terraform starts. **No Linux Terraform init/validate result exists.** No distribution was created/reset or container used. |
| Isolated `.tools/mtls-minimal/main.tf`, only exact Terraform/provider constraints, no provider configuration/backend/resources | Mirror init exit 1 because sandbox cannot checksum the archive (Access denied). This is not a successful init. Copying the existing exact provider cache, keeping the original lockfile, permits the separate validate experiment; validate exits 1 at plugin TLS. No constraint or lock change. |
| Direct launch of the exact installed AWS provider binary | SHA256 of installed binary equals the member extracted from the already-checksum-verified official 6.74.0 release archive. Plugin starts with its public protocol cookie and a freshly generated ephemeral client certificate; no provider RPC or cloud configuration sent. |
| Direct Python TLS to the plugin-advertised loopback address | Sole trust root is the exact certificate advertised by this plugin process; client certificate supplied and server verification mandatory. Fails certificate verification: unable to get local issuer certificate. |
| Verify advertised server certificate offline | It is a self-issued CA certificate, its self-signature verifies, and `openssl verify -CAfile <advertised-cert> <advertised-cert>` exits 0. |
| Independent OpenSSL client using `-verify_return_error`, sole advertised CA and ephemeral client certificate | Exits 1, certificate validation error 20 at depth 0. No `-noverify` or insecure option. |
| PyOpenSSL verification callback with `VERIFY_PEER`, sole advertised CA and client certificate | Callback records the offered depth-0 certificate, then returns the **original verification result unchanged**, so failure remains fatal. Offered certificate SHA256 differs from the plugin-advertised certificate; offered certificate is not self-issued and its issuer differs from the advertised certificate. Handshake fails. No accepted unverified connection. |

The original ignored diagnostic exits 0 only because its purpose was to collect a structured failed-handshake result; it does **not** mean Terraform validation or TLS passed. The reproducible tracked helper instead exits **1** when verified TLS fails or substitution is observed, **2** when the diagnostic itself cannot complete, and **0** only when verified pinned TLS succeeds without observed substitution. Its actual run here exited 1 and reproduced the same substitution evidence. All diagnostic provider processes were terminated after capture; no cloud calls were made.

## Finding and limit

A substituted TLS certificate is presented on the local provider connection. This explains why the pinned plugin certificate cannot validate it. The evidence isolates the failure from resume/site code and from Terraform's HCL evaluator: it reproduces with a direct provider connection and a minimal configuration while the core-only control succeeds. It does not identify the component performing substitution, establish its policy owner, distinguish a sandbox mechanism from endpoint/network instrumentation, or prove that an alternative execution boundary is unaffected. The native outside-sandbox comparison still failed, and the Ubuntu attempt did not reach Terraform.

HashiCorp go-plugin AutoMTLS adds the plugin-advertised certificate directly to a new per-connection root pool, rather than using the operating-system CA pool. Importing an enterprise/system CA into normal TLS trust therefore does not repair this pinned mutual-authentication channel. Trusting the substituted certificate, disabling verification/mTLS, altering provider pins/locks, or disabling endpoint protection would weaken the control and was not attempted.

The legitimate next step is validation in an approved environment that preserves the plugin's end-to-end mutually authenticated loopback channel, or a policy-owner-approved narrowly scoped resolution that preserves that property. No such successful environment is claimed here. The orchestrator separately records the human-authorized Terraform-only outside-sandbox comparison. Until both real root validations succeed without weakened controls, local validation remains blocked.

## Reproduction and sources

Tracked helper [`scripts/diagnose-provider-mtls.py`](../scripts/diagnose-provider-mtls.py) reproduces the Windows direct-provider test in a fresh checkout with Python, `cryptography` and `PyOpenSSL` installed in a separately selected trusted diagnostic environment. The actual diagnostic Python used cryptography 39.0.1 and PyOpenSSL 23.0.0 already installed on this host; these are diagnostic observations, not a recommendation to downgrade current packages. No dependency or production-runtime change is required by the helper.

First acquire the exact AWS 6.74.0 Windows provider archive and its official SHA256SUMS over verified TLS from [HashiCorp releases](https://releases.hashicorp.com/terraform-provider-aws/6.74.0/), and the matching installed executable from readonly-locked provider initialization. It verifies the archive checksum against the supplied manifest and the executable against the archive member **before execution**. This checks release-checksum consistency; independent publisher-signature verification is not claimed.

```text
python scripts/diagnose-provider-mtls.py --provider <exact-provider-executable> --archive <official-6.74.0-windows_amd64.zip> --checksums <official-SHA256SUMS>
```

Defaults match this checkout's existing ignored provider mirror/cache paths; with those prerequisites, `python scripts/diagnose-provider-mtls.py` suffices. The helper is Windows-only and refuses non-loopback plugin endpoints or unexpected provider filenames. It strips inherited cloud/provider environment variables from its child, sends no provider RPC, writes no certificate/key/debug logs, prints sanitized status/booleans only, bounds process/handshake waits and deletes its ephemeral certificate/key directory on exit. A verification callback returns the original verification outcome unchanged. It never trusts a substituted certificate or overrides a failed chain validation.

Ignored original helpers `.tools/diagnose-minimal.py` and `.tools/diagnose-direct-mtls.py` retain private initial raw evidence; the tracked helper supersedes them for portable reproduction. The minimal project also preserves the exact constraints/lock. Sanitized structured findings are summarized above rather than exposing certificate material or process environment values.

Primary sources inspected: [Terraform 1.17.2 plugin handshake](https://github.com/hashicorp/terraform/blob/v1.17.2/internal/plugin/serve.go), [Terraform 1.17.2 dependency versions](https://github.com/hashicorp/terraform/blob/v1.17.2/go.mod), [go-plugin v1.7.0 client certificate loading](https://github.com/hashicorp/go-plugin/blob/v1.7.0/client.go), [go-plugin v1.7.0 server AutoMTLS](https://github.com/hashicorp/go-plugin/blob/v1.7.0/server.go), [go-plugin certificate generation](https://github.com/hashicorp/go-plugin/blob/v1.7.0/mtls.go). AutoMTLS requires peer certificates from that process-specific handshake; Windows go-plugin uses TCP loopback, so Unix-socket transport is not an available supported switch here.
