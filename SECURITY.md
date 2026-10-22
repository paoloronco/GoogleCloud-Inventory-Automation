# Security policy

This repository contains source code for a read-only inventory collector. Please report potential vulnerabilities privately using GitHub's private vulnerability reporting feature where available, rather than opening a public issue containing secrets or private infrastructure data.

Do not commit service-account JSON keys, GitHub tokens, bucket objects, secret values, or generated private inventory. Use the attached Cloud Run service account and Google Secret Manager for credentials.

The collector's security-review notes are heuristic observations, not confirmed vulnerabilities. Review the IAM permissions, output repository access and token expiry before enabling unattended execution.
