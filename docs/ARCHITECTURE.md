# Architecture and data model

The active collector is a Cloud Run Job in `inventory-512409` (`europe-west1`). Its attached service account reads resource metadata from 14 allowlisted projects across two Google accounts. A GitHub fine-grained token is injected from Secret Manager for publishing to the private output repository.

## Collection flow

1. `gcloud asset search-all-resources` retrieves resource metadata.
2. `gcloud services list --enabled` retrieves enabled APIs separately.
3. Optional Deep Analysis reads selected Cloud Run, firewall, bucket, service-account and IAM metadata.
4. The classification layer groups known workloads/data, configuration, system and unknown asset types.
5. Reporting creates Markdown and an XLSX workbook per account; the raw JSON snapshot is preserved.
6. GitHub Contents API updates changed files on `main` sequentially.

## Output namespaces

- `accounts/paolo.ronco2000/`: six allowlisted projects.
- `accounts/paolo.ronco20/`: eight allowlisted projects.
- `accounts/primary/` and `accounts/secondary/`: historical v7 output, not current destinations.

Each current account directory includes `README.md`, `inventory.json`, `inventory.xlsx`, `projects/*.md` and `deep/*.md`. `CHANGES.md` appears after a subsequent snapshot comparison.

## Resource semantics

A Cloud Asset Inventory asset is not necessarily a deployed application. The v8 taxonomy explicitly recognizes selected resource types; unknown assets remain unclassified. Some resources can represent multiple views of the same logical workload (e.g. Cloud Functions and backing Cloud Run services). The overview therefore reports indicative counts, not unique application counts.

## Security boundaries

Collector IAM uses project-local custom roles. No service-account key is stored. No secret values, bucket object contents or application source are collected. Security observations are heuristic and cannot establish effective external reachability. Reports must remain private.

## Limitations

The publisher is not transactional. The diff excludes some transient Cloud Run assets but not all ephemeral metadata. Full dependency mapping, source reconstruction, effective-access analysis and automatic remediation are not implemented. Cloud Scheduler is not yet enabled.
