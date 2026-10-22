# Google Cloud Inventory

Read-only Google Cloud inventory collector built with Python and deployed as a Cloud Run Job. It separates known workloads and data stores from configuration assets, system resources, unclassified assets and enabled APIs. Reports are published to the private [GCP-Inventory](https://github.com/paoloronco/GCP-Inventory) repository.

## Current deployment

| Component | Status |
|---|---|
| Collector | **v8** — built, deployed and manually validated |
| Google Cloud projects | **14** across two account scopes (6 + 8) |
| Runtime | Cloud Run Job `gcp-inventory-test` |
| Host project / region | `inventory-512409` / `europe-west1` |
| GitHub branch | `main` |
| Output | Markdown, JSON and one Excel workbook per account |
| IAM | Project-local custom role `gcpInventoryCollector` for collection |
| Cloud Scheduler | **Not configured** |

Cloud Run, Cloud Build, Artifact Registry, Secret Manager and API usage can incur charges.

## Architecture

```text
Cloud Run Job (Python + gcloud, attached service account)
  ├── Cloud Asset Inventory: resource metadata
  ├── Service Usage: enabled APIs
  ├── Optional deep collectors: Cloud Run, firewall, buckets, IAM
  ├── Classification / Markdown / XLSX / change comparison
  └── GitHub Contents API (fine-grained token from Secret Manager)
       └── Private GCP-Inventory repository
           ├── accounts/paolo.ronco2000/   (6 projects)
           └── accounts/paolo.ronco20/     (8 projects)
```

Project scopes are explicit allowlists; the collector does not automatically enumerate all projects visible to a Google account. The account directory is an output namespace, not a proof of ownership.

## Output per account

| Path | Contents |
|---|---|
| `README.md` | Project overview with separated asset counts |
| `inventory.xlsx` | Overview, Resources, Networking, IAM, Enabled APIs, Security Review and Raw Inventory |
| `inventory.json` | Full collected metadata snapshot |
| `projects/<project-id>.md` | Grouped resource report for each project |
| `deep/<project-id>.md` | Configuration metadata and heuristic security review |
| `CHANGES.md` | Comparison with the previous published snapshot, from the second publication onward |

The old `accounts/primary/` and `accounts/secondary/` directories are retained as historical outputs. They are not current v8 destinations.

**Counts are not workload counts.** Cloud Asset Inventory includes administrative and Google-managed objects. The classifier uses a conservative type allowlist: unknown types remain unclassified. A Cloud Function and its backing Cloud Run service may represent the same logical workload but currently appear separately.

## Quick start: tests

```bash
git switch main
git pull --ff-only origin main
python3 -m venv .venv
. .venv/bin/activate
pip install -r cloudrun/requirements.txt
PYTHONPATH=cloudrun python3 -m unittest discover -s cloudrun -p 'test_*.py' -v
python3 -m py_compile cloudrun/*.py
```

The v8 release passed 11 unit tests and dry-run collection for both account scopes. Unit tests use mocks and are not a substitute for live validation.

## Deployment and operation

See [Operations](docs/OPERATIONS.md) for deployment, explicit per-account scopes, dry-run, publishing, logging and rollback.

Environment variables:

| Name | Description |
|---|---|
| `PROJECT_SCOPE` | Explicit comma-separated list of project IDs |
| `INVENTORY_IDENTITY` | `paolo.ronco2000` or `paolo.ronco20` |
| `DRY_RUN` | `true` avoids GitHub writes |
| `DEEP_SCAN` | `true` enables optional configuration collectors |
| `GITHUB_REPOSITORY` | Output repository (`paoloronco/GCP-Inventory`) |
| `GITHUB_BRANCH` | Output branch (`main`) |
| `GITHUB_TOKEN` | Fine-grained token injected from Secret Manager |

Legacy values `primary` and `secondary` are mapped to the named account directories by v8. Do not use them for new deployment documentation.

## Source layout

| Path | Purpose |
|---|---|
| `cloudrun/job.py` | Collection and GitHub publication |
| `cloudrun/classification.py` | Conservative resource taxonomy |
| `cloudrun/reporting.py` | Markdown reports and change comparison |
| `cloudrun/excel_report.py` | Excel workbook generation |
| `cloudrun/deep.py` | Optional configuration collectors |
| `cloudrun/observations.py` | Security-review heuristics |
| `cloudrun/test_*.py` | Unit tests |
| `inventory/` | Legacy exporter, not the Cloud Run entrypoint |
| `docs/archive/` | Historical design notes |

## Limitations

- No full dependency graph, effective-access audit, source-code analysis or automated remediation.
- Security-review observations do not establish exploitable vulnerabilities.
- Some asset types remain unclassified and workload counts may double-count underlying managed services.
- JSON and Excel contain resource metadata, not bucket object contents, secret values or application source code.
- The publisher updates GitHub files sequentially; publication is not atomic and may generate multiple commits.
- `CHANGES.md` shows the latest comparison, not an immutable historical event stream.
- No Cloud Scheduler schedule has been activated. The legacy workflow in the output repository must be reviewed before scheduling.

## Documentation

[Architecture](docs/ARCHITECTURE.md) · [Operations](docs/OPERATIONS.md) · [Inventory classification](docs/INVENTORY_V8.md) · [Excel and migration](docs/EXCEL_AND_MIGRATION_V8.md) · [Roadmap](docs/ROADMAP.md) · [Security](SECURITY.md)

## License

[MIT](LICENSE).
