# Operations

This guide documents the **currently tested** Cloud Run deployment. Nothing in this file creates a schedule.

## Current deployment

| Setting | Value |
|---|---|
| Host project | `inventory-512409` |
| Region | `europe-west1` |
| Artifact Registry | `gcp-inventory` |
| Cloud Run Job | `gcp-inventory-test` |
| Runtime service account | `gcp-inventory-runner@inventory-512409.iam.gserviceaccount.com` |
| GitHub secret | `github-inventory-token` (Secret Manager) |
| Private destination | `paoloronco/GCP-Inventory`, branch `master` |
| Scheduled execution | Not configured |

## Verify deployed configuration

```bash
gcloud config set project inventory-512409
gcloud run jobs describe gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --format='yaml(spec.template.spec.template.spec.containers)'
```

This displays environment variable names and secret references, not secret contents. Check `DRY_RUN` before execution.

## Test code

```bash
git pull origin master
PYTHONPATH=cloudrun python3 -m unittest discover -s cloudrun -p 'test_*.py' -v
python3 -m py_compile cloudrun/*.py
```

## Build and deploy a new version

Replace `VERSION` with a **new** tag; do not overwrite a previous tag.

```bash
gcloud builds submit --project=inventory-512409 \
  --tag=europe-west1-docker.pkg.dev/inventory-512409/gcp-inventory/collector:VERSION

gcloud run jobs update gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --image=europe-west1-docker.pkg.dev/inventory-512409/gcp-inventory/collector:VERSION \
  --update-env-vars=DRY_RUN=true,DEEP_SCAN=false
```

## Manual verification

```bash
gcloud run jobs execute gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --update-env-vars=DRY_RUN=true,DEEP_SCAN=true --wait
```

Check the latest execution and structured logs. A successful exit means mandatory collection completed; review `deepResults.errors` separately because optional collectors can fail without failing the job.

```bash
gcloud run jobs executions list --job=gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 --limit=5

gcloud logging read \
  'resource.type="cloud_run_job" AND resource.labels.job_name="gcp-inventory-test" AND jsonPayload.deepResults:*' \
  --project=inventory-512409 --limit=1 --format='json(jsonPayload)'
```

Only after reviewing the results, publish once manually:

```bash
gcloud run jobs execute gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --update-env-vars=DRY_RUN=false,DEEP_SCAN=true --wait
```

This execution **writes to the private GitHub repository**. It does not change the stored job default.

## Rollback

Use a previously tested image tag, for example `collector:v7`, and leave dry-run enabled. Do not delete previous images until the replacement is validated.

```bash
gcloud run jobs update gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --image=europe-west1-docker.pkg.dev/inventory-512409/gcp-inventory/collector:v7 \
  --update-env-vars=DRY_RUN=true,DEEP_SCAN=false
```

## Troubleshooting

- Exit code 2: mandatory Cloud Asset Inventory or enabled-API collection failed; inspect `jsonPayload.status="incomplete"`.
- Successful job with partial deep report: inspect `deepResults.errors`, missing permissions and disabled APIs.
- No new GitHub commit: check `DRY_RUN`, token scope, output equality and structured logs.
- Cloud Shell disconnects do not necessarily stop Cloud Run Jobs; inspect the execution directly.
- GitHub token expiry requires a new Secret Manager version and job secret reference review.
- Never paste token values, full secret payloads or private IAM principal lists into public issues.

## Later work

Scheduler configuration, dedicated invocation identity, least-privilege IAM role redesign, multi-account separation and alerts are intentionally deferred.
