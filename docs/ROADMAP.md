# Roadmap and known limitations

## Completed

- Cloud Run Jobs collector v8 deployed and tested.
- 14 projects across two explicit account scopes.
- Project-local eight-permission collector IAM roles; successful Deep Analysis on both account scopes.
- Grouped Markdown inventory, raw JSON and per-account Excel workbooks.
- Published reports on GitHub branch `main`.

## Before scheduling

- Update the private repository's root README to link the current account directories and all 14 projects.
- Improve classification of unknown asset types and deduplicate logical workloads such as Cloud Functions with backing Cloud Run services.
- Validate the XLSX content and filters in a spreadsheet viewer, not only file presence.
- Reduce GitHub commit noise and improve durable change history.
- Create dedicated Scheduler invocation identities and independently scoped daily/weekly jobs with monitoring and failure alerts.

## Later

- More detailed resource dependency maps and configuration relationships.
- Optional n8n notifications and AI-assisted summaries.
- Account/project discovery with explicit approval and deduplication.

## Out of scope today

Full CSPM, effective IAM access graph, application source-code extraction, secret contents and automatic remediation.
