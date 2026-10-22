# Resource taxonomy v9

The v9 classification maps asset types observed in both v8 account snapshots to explicit categories. It does not alter Cloud Asset Inventory collection, IAM, GitHub publishing, or raw JSON.

New categories include Build & Artifacts, Messaging & Events, Observability and Project Metadata. Service Usage assets are separated from actual resources. Routes, subnetworks and firewall rules are configuration, not workloads. Image versions, revisions, execution records, service-account keys and backups are recorded as supporting/system assets; their existence can still matter for security or cost.

## Logical workload matching

Cloud Functions and Cloud Run Services can represent one deployment. The v9 report shows **possible** duplicate pairs only when name, project and region all match. This is an estimate, not proof of ownership or full deduplication. Raw asset entries are never discarded.

## Validation

Run all tests and compare v8/v9 reports for both account scopes. In particular, verify that unclassified counts decline without inflating the primary workload count. Do not merge or deploy without checking actual report output. The workbook uses the same classifier and will pick up the expanded categories.

## Limitations

The matching cannot confirm whether a Cloud Run service is managed by a Cloud Function without additional metadata. Unknown asset types remain unclassified. Resource state, cost, actual use and internet exposure are not inferred from the type alone.
