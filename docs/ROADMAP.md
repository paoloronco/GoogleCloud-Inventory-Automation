# Limitations and roadmap

## Before scheduling

- Normalize ephemeral resources in published snapshots and report counts, to avoid commits without material infrastructure changes.
- Improve change reporting with a durable history and scan metadata, distinguishing collection success, partial optional collection and API-not-enabled states.
- Audit and narrow IAM permissions. Broad predefined viewer roles were used to validate collectors and should not be treated as final least-privilege configuration.
- Add failure alerting, bounded retries, concurrency protection and token-expiry handling.
- Validate one dry-run and one manual publication after any collector change.
- Review legacy GitHub Actions workflow in the private repository; it has its own cron and must not be confused with Cloud Scheduler.

## Later

- Cloud Scheduler: separate daily standard and weekly deep invocations, explicit timezone, invocation-only identity.
- Multi-account: separate identities and project scopes, project-number deduplication, independent failure reporting.
- Resource relationships and richer per-service configuration coverage.
- Optional n8n summaries and notifications.

## Not implemented

Full IaC/source-code reconstruction, complete CSPM findings, exhaustive IAM effective-access analysis, or automated remediation.
