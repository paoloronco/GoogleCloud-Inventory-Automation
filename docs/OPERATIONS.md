# Operations — Cloud Run collector v8

## Deployment inventory

| Setting | Value |
|---|---|
| Host project | `inventory-512409` |
| Region | `europe-west1` |
| Cloud Run Job | `gcp-inventory-test` |
| Container image | `europe-west1-docker.pkg.dev/inventory-512409/gcp-inventory/collector:v8` |
| Runtime service account | `gcp-inventory-runner@inventory-512409.iam.gserviceaccount.com` |
| GitHub secret | `github-inventory-token` in Secret Manager |
| Output repository | `paoloronco/GCP-Inventory`, branch `main` |
| Scheduler | Not configured |

## Account scopes

**paolo.ronco2000** (6 projects):

```text
cloud-digitalleader,gen-lang-client-0665756019,inventory-512409,orbipage-saas,paolo-ronco-website-app,sito-351310
```

**paolo.ronco20** (8 projects):

```text
gen-lang-client-0751722395,github-pronco,makecom-wp-voiceovers,pr-homelab,pr-n8n-workflows,prhomelab-ai,spotifyyt-pr,tabsessionsaver
```

## Inspect the job

```bash
gcloud run jobs describe gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --format='yaml(spec.template.spec.template.spec.containers)'
```

Check the configured `PROJECT_SCOPE`, `GITHUB_BRANCH=main`, `DRY_RUN=true` and secret reference. Do not assume an execution override changes the stored job defaults.

## Dry-run: first account

```bash
gcloud run jobs execute gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --update-env-vars=INVENTORY_IDENTITY=paolo.ronco2000,DRY_RUN=true,DEEP_SCAN=true \
  --wait
```

This relies on the stored six-project scope. Verify it with `jobs describe` before execution.

## Dry-run: second account

```bash
gcloud run jobs execute gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --update-env-vars='^@^INVENTORY_IDENTITY=paolo.ronco20@PROJECT_SCOPE=gen-lang-client-0751722395,github-pronco,makecom-wp-voiceovers,pr-homelab,pr-n8n-workflows,prhomelab-ai,spotifyyt-pr,tabsessionsaver@DRY_RUN=true@DEEP_SCAN=true' \
  --wait
```

The `^@^` delimiter is required here because the project list contains commas.

## Publish manually

After validating each dry-run, repeat the corresponding command with `DRY_RUN=false`. Publishing writes to the private GitHub repository. Run one identity at a time, not concurrently. Keep the stored job default `DRY_RUN=true`.

## Validate the execution

```bash
gcloud run jobs executions list \
  --job=gcp-inventory-test --project=inventory-512409 \
  --region=europe-west1 --limit=5

gcloud logging read \
  'resource.type="cloud_run_job" AND resource.labels.job_name="gcp-inventory-test" AND jsonPayload.deepResults:*' \
  --project=inventory-512409 --limit=5 --format='json(jsonPayload)'
```

A successful exit confirms mandatory collection, not necessarily every optional deep collector. Inspect each `deepResults.errors` array. Disabled APIs can be reported as not enabled rather than errors.

## Build and deploy

```bash
git switch main
git pull --ff-only origin main
PYTHONPATH=cloudrun python3 -m unittest discover -s cloudrun -p 'test_*.py' -v

gcloud builds submit --project=inventory-512409 \
  --tag=europe-west1-docker.pkg.dev/inventory-512409/gcp-inventory/collector:VERSION

gcloud run jobs update gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --image=europe-west1-docker.pkg.dev/inventory-512409/gcp-inventory/collector:VERSION \
  --update-env-vars=DRY_RUN=true,DEEP_SCAN=false
```

Replace `VERSION` with a new immutable version tag.

## Rollback

```bash
gcloud run jobs update gcp-inventory-test \
  --project=inventory-512409 --region=europe-west1 \
  --image=europe-west1-docker.pkg.dev/inventory-512409/gcp-inventory/collector:v7 \
  --update-env-vars=DRY_RUN=true,DEEP_SCAN=false
```

Note that v7 writes under the legacy `primary`/`secondary` namespace, so review output paths before publishing after rollback.

## IAM

Each of the 14 target projects has a local `gcpInventoryCollector` custom role assigned to the central service account. It includes eight collector permissions: `cloudasset.assets.searchAllResources`, `compute.firewalls.list`, `iam.serviceAccounts.list`, `resourcemanager.projects.get`, `resourcemanager.projects.getIamPolicy`, `run.services.list`, `serviceusage.services.list`, `storage.buckets.list`. The token access grant is scoped to its Secret Manager secret.

## Troubleshooting

- `status=incomplete`: mandatory resource/API collection failed; inspect structured failures.
- Deep collector errors: inspect `deepResults.errors`; a successful job exit does not rule them out.
- No new GitHub commit: check `DRY_RUN`, identity path, branch, token permissions and content equality.
- Cloud Shell disconnects do not necessarily interrupt Cloud Run execution.
- Secret Manager token rotation requires reviewing the job's secret version reference.
- Avoid sharing private resource metadata or secrets in public issues.

## Before enabling scheduling

The legacy GitHub Actions cron has been removed. Configure separate explicit scopes for both accounts, minimum-privilege Scheduler invocation and failure notifications. Cloud Scheduler is not yet configured.
