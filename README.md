# Google Cloud Inventory

Read-only inventory collection, configuration summaries and change reporting for Google Cloud projects. The collector runs as a **Cloud Run Job** and publishes Markdown and JSON to a separate private GitHub repository.

This repository contains **source code and deployment documentation only**. Collected infrastructure data belongs in the private [GCP-Inventory](https://github.com/paoloronco/GCP-Inventory) repository.

## Current status

- Cloud Run collector v7 has been built and manually tested against six projects.
- Standard inventory, per-project reports, basic deep inspection and change reports have been published successfully.
- **Cloud Scheduler is not configured**; runs are manual.
- Multi-account discovery and relationship mapping are **not implemented**.
- The older GitHub Actions/Excel exporter is retained for reference, not the recommended deployment path.
- Cloud Run, Artifact Registry, Cloud Build, Secret Manager and APIs may incur charges. This is **not** a zero-cost guarantee.

## How it works

```text
Cloud Run Job (Python + gcloud)
  ├── Cloud Asset Inventory / enabled APIs
  ├── Optional deep collectors (IAM, Cloud Run, firewall, buckets)
  └── GitHub Contents API
       └── Private GCP-Inventory repository
           ├── accounts/primary/inventory.json
           ├── accounts/primary/README.md
           ├── accounts/primary/projects/*.md
           ├── accounts/primary/deep/*.md
           └── accounts/primary/CHANGES.md
```

The runtime uses a dedicated Google Cloud service account. The GitHub fine-grained token is supplied through Secret Manager. No service-account JSON key is required.

## Run locally

Requires Python 3, `gcloud` CLI, and appropriate read-only access to the selected projects. Install dependencies for local Python tooling if needed:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r cloudrun/requirements.txt
PYTHONPATH=cloudrun python3 -m unittest discover -s cloudrun -p 'test_*.py' -v
python3 -m py_compile cloudrun/*.py
```

The tests use mocked responses and do not prove permissions or API compatibility in a live environment.

## Deploy and operate

See [deployment and operations](docs/OPERATIONS.md) for verified project-specific commands, dry-run procedure, troubleshooting and rollback. The container image is built from the root [Dockerfile](Dockerfile).

For the current environment, the host project is `inventory-512409`, region `europe-west1`, job `gcp-inventory-test`, and runtime identity `gcp-inventory-runner@inventory-512409.iam.gserviceaccount.com`. These are deployment details, not hardcoded requirements.

Key settings:

| Environment variable | Purpose |
|---|---|
| `PROJECT_SCOPE` | Explicit comma-separated project allowlist |
| `INVENTORY_IDENTITY` | Output namespace, currently `primary` |
| `DEEP_SCAN` | Enable optional configuration collectors |
| `DRY_RUN` | Defaults to true; no GitHub writes |
| `GITHUB_REPOSITORY` | Private output repository |
| `GITHUB_BRANCH` | Destination branch |
| `GITHUB_TOKEN` | Secret Manager injection; required only for publishing |

## Repository layout

| Path | Purpose |
|---|---|
| `cloudrun/job.py` | Collection orchestration and GitHub publishing |
| `cloudrun/deep.py` | Optional read-only configuration collection |
| `cloudrun/reporting.py` | Markdown reports and resource differences |
| `cloudrun/observations.py` | Limited security-review heuristics |
| `cloudrun/test_*.py` | Unit tests |
| `inventory/` | Legacy and experimental exporters; not the Cloud Run entrypoint |
| `docs/` | Architecture, operations, limitations and migration notes |
| `.github/workflows/*.example` | Inactive legacy examples; not deployed workflows |

## Limitations and security

- This is **inventory**, not a comprehensive security assessment or a substitute for CSPM.
- Resource names, IAM role summaries and network ranges are operational metadata; keep reports private.
- The current deep collectors do not retrieve application source, secret values, bucket objects or environment variables.
- Disabled APIs are marked as not enabled; unavailable permissions are reported as collector errors.
- The JSON inventory includes ephemeral assets; the change comparison suppresses Cloud Run executions/tasks, but other ephemeral artifacts can still generate commits.
- Publishing uses sequential GitHub Contents API updates, not one atomic commit. A partial publication is possible if a later write fails.
- Do not run multiple publishing jobs against the same account namespace concurrently.
- Review broad predefined read-only IAM grants before production scheduling.

## Documentation

- [Architecture and data model](docs/ARCHITECTURE.md)
- [Deployment, manual tests and rollback](docs/OPERATIONS.md)
- [Known limitations and next steps](docs/ROADMAP.md)
- [Security policy](SECURITY.md)

## License

[MIT](LICENSE). Maintained by Paolo Ronco.
