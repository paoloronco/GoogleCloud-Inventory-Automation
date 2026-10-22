# Architecture and data model

The active collector runs inside Cloud Run Jobs, using the attached service account to call Google Cloud APIs. A fine-grained GitHub token is injected through Secret Manager only for publishing to the private repository.

The current project list is an explicit `PROJECT_SCOPE` allowlist, **not** automatic account-wide discovery. One namespace (`primary`) represents the first Google account's approved projects; a second identity is not yet configured.

## Collection

1. Cloud Asset Inventory searches resource metadata for each selected project.
2. Service Usage lists enabled APIs.
3. With `DEEP_SCAN=true`, optional collectors read limited metadata for Cloud Run, firewall rules, buckets, service accounts and IAM role summaries.
4. Reporting builds per-project Markdown and a summary.
5. GitHub publishing compares existing file contents and writes only changed files.

## Outputs

`accounts/primary/inventory.json` is the current full resource/API snapshot. `projects/*.md` lists resources and API names; `deep/*.md` contains the optional configuration summaries and heuristic review notes; `CHANGES.md` compares the last two published snapshots.

These are **latest-state files**, not a dated immutable snapshot archive. Git commit history preserves prior versions, but there is no separate indexed change-history collection.

## Boundaries

The collector does not inspect application source code, bucket object contents, secret values or container images. It does not prove external reachability, effective IAM privilege, security compliance or resource dependency graphs. Cloud Run Execution and Task assets are excluded from diff comparison, but may still change the raw JSON and Markdown reports.
