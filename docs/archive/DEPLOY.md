# Cloud Run deployment — manual, no schedule by default

## Prerequisites
Use a new project `pr-cloud-inventory` with billing linked. Run from Google Cloud Shell with an authenticated administrator. Replace placeholders, and review IAM grants before execution.

1. Enable APIs: `gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com cloudscheduler.googleapis.com secretmanager.googleapis.com --project=pr-cloud-inventory`.
2. Create an Artifact Registry Docker repository and a runtime service account in `pr-cloud-inventory`.
3. Grant that runtime service account read access to the **explicitly selected** project IDs in both environments: `roles/cloudasset.viewer`, `roles/serviceusage.serviceUsageViewer` and any additional narrow permissions for deep inspection. Verify each binding against least privilege. Cross-project IAM grants require an administrator in each account's environment.
4. Create a fine-grained GitHub token limited to `paoloronco/GCP-Inventory`, Contents read/write. Store it in Secret Manager. Grant only `roles/secretmanager.secretAccessor` on that secret to the runtime service account. Rotate and audit it periodically.
5. Build image: `gcloud builds submit --tag REGION-docker.pkg.dev/pr-cloud-inventory/REPOSITORY/gcp-inventory:VERSION . --project=pr-cloud-inventory`.
6. Create job (manual only): `gcloud run jobs create gcp-inventory --image=IMAGE --region=REGION --project=pr-cloud-inventory --service-account=SERVICE_ACCOUNT --set-env-vars=INVENTORY_IDENTITY=primary,PROJECT_SCOPE=PROJECT1\\,PROJECT2,GITHUB_REPOSITORY=paoloronco/GCP-Inventory --set-secrets=GITHUB_TOKEN=SECRET_NAME:latest --tasks=1 --max-retries=0`. For project lists containing commas, prefer a YAML env file with `--env-vars-file` instead of the example inline flags.
7. Test: `gcloud run jobs execute gcp-inventory --region=REGION --project=pr-cloud-inventory --wait`. Inspect Cloud Logging and private GitHub repo.
8. Only after validating both access domains, add a second job/identity or expand the approved allowlist. Set `DEEP_SCAN=true` for a separate weekly job.

## Scheduler — deliberately not created
After manual acceptance, create Cloud Scheduler jobs targeting the Cloud Run Jobs execution API using an invocation-only service account (`roles/run.invoker` on the job). Keep the schedules paused until explicitly approved. Scheduler has its own pricing; consult current billing/free-tier conditions.

## Operational limitations
This is a first deployment slice. The collector currently accepts explicit project IDs rather than discovering all projects. Deep checks record counts only, not configuration payloads. GitHub updates use the Contents API and are not atomic across multiple files. Run one job at a time per identity to avoid concurrent writes. Review token storage, resource names, billing alerts and permissions before launch.
