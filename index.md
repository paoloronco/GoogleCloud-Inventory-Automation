# GCP Cloud Inventory Automation (Zero Cost)

This project provides an **end-to-end, production-grade way to automatically generate a Google Cloud inventory** with **zero GCP cost**, **no static credentials**, and **no manual updates**.

It is designed to be:
- Secure by default (OIDC, no JSON keys)
- Cheap (read-only APIs, no paid services)
- Transparent (inventory committed to Git)
- Easy to extend (Python + GitHub Actions)

The result is a continuously updated **Excel / CSV cloud inventory** generated on a schedule.

---

## What this project does

On a fixed schedule (or manually), GitHub Actions:
1. Authenticates to Google Cloud using **Workload Identity Federation (OIDC)**
2. Impersonates a **read-only Service Account**
3. Queries **Cloud Asset Inventory** and **Service Usage API**
4. Generates:
   - `inventory.xlsx`
   - `inventory_projects.csv`
   - `inventory_resources.csv`
   - `inventory_apis.csv`
5. Commits changes automatically if anything has changed

No credentials are stored in the repository. No GCP services that generate cost are required.

---

## High-level architecture

```
GitHub Actions (cron / manual)
        │
        ▼
Workload Identity Federation (OIDC)
        │
        ▼
Service Account (read-only)
        │
        ▼
Cloud Asset Inventory + Service Usage API
        │
        ▼
Excel / CSV inventory (auto-commit)
```

Key properties:
- No service account keys
- Authentication restricted per-repository
- Minimal IAM permissions
- Full audit trail via Git

---

## Prerequisites

You need:
- A Google Cloud account with one or more projects
- A GitHub account
- Permissions to:
  - Create service accounts
  - Modify IAM policies on projects
  - Create Workload Identity Pools and Providers

This setup works **without** an Organization or Folder, but supports them if present.

---

## Step 1 – Create the Service Account

This service account will be used **only** for inventory collection.

```bash
gcloud iam service-accounts create inventory-bot \
  --project YOUR_PROJECT_ID \
  --display-name "Cloud Inventory Bot"
```

Why this exists:
- Separation between human users and automation
- Easy permission auditing
- Easy revocation

---

## Step 2 – Grant read-only permissions on projects

Because this setup does not rely on an Organization or Folder, permissions are granted **per project**.

### Required roles

| Role | Purpose |
|----|----|
| `roles/viewer` | Read access to project resources |
| `roles/cloudasset.viewer` | Access Cloud Asset Inventory |
| `roles/serviceusage.serviceUsageViewer` | List enabled APIs |

### Apply roles to all projects

```bash
SA="serviceAccount:inventory-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com"

for P in $(gcloud projects list --format="value(projectId)"); do
  gcloud projects add-iam-policy-binding "$P" \
    --member="$SA" \
    --role="roles/viewer"

  gcloud projects add-iam-policy-binding "$P" \
    --member="$SA" \
    --role="roles/cloudasset.viewer"

  gcloud projects add-iam-policy-binding "$P" \
    --member="$SA" \
    --role="roles/serviceusage.serviceUsageViewer"
done
```

If you add new projects later, simply re-run this script.

---

## Step 3 – Configure Workload Identity Federation (GitHub → GCP)

### Create a Workload Identity Pool

- Pool name: `github-pool`
- Provider type: **OIDC**
- Issuer: GitHub

### Attribute mapping

```text
google.subject = assertion.sub
attribute.repository = assertion.repository
attribute.ref = assertion.ref
```

### Attribute condition (repository allowlist)

```text
attribute.repository == "OWNER/REPOSITORY_NAME"
```

This ensures **only the specified GitHub repository** can authenticate.

---

## Step 4 – Allow the repository to impersonate the Service Account

### Allow Workload Identity impersonation

```bash
gcloud iam service-accounts add-iam-policy-binding \
  inventory-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --project YOUR_PROJECT_ID \
  --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/OWNER/REPOSITORY_NAME"
```

### Allow token generation (required by gcloud)

```bash
gcloud iam service-accounts add-iam-policy-binding \
  inventory-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --project YOUR_PROJECT_ID \
  --role roles/iam.serviceAccountTokenCreator \
  --member "principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/OWNER/REPOSITORY_NAME"
```

Both bindings are required.

---

## Step 5 – Configure GitHub Secrets

In your GitHub repository:

**Settings → Secrets and variables → Actions → Secrets**

| Name | Value |
|----|----|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/PROVIDER_NAME` |
| `GCP_SERVICE_ACCOUNT` | `inventory-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com` |

No credentials or tokens are committed to the repository.

---

## Repository structure

```
.github/workflows/cloud-inventory.yml.example
inventory/
  export_inventory.py
  projects.txt
  requirements.txt
inventory.xlsx   (generated)
```

> The `.example` workflow does **not** run automatically.
> Rename it to `cloud-inventory.yml` to enable execution.

---

## projects.txt

This file explicitly defines which projects are inventoried:

```text
project-a
project-b
project-c
```

This avoids relying on global project listing permissions and keeps scope explicit.

---

## Inventory script

The Python script:
- Reads `projects.txt`
- Queries Cloud Asset Inventory using `--asset-types`
- Queries enabled APIs per project
- Produces Excel and CSV outputs

Important implementation detail:
- Resource filtering is done via `--asset-types`, not query filters

---

## GitHub Actions workflow

Key properties:
- Uses OIDC authentication
- Requires only `id-token: write` and `contents: write`
- Commits output only when changes are detected

Schedule:
```yaml
cron: "0 6 * * *"
```

Runs daily at **06:00 UTC**.

---

## Result

You get:
- A continuously updated cloud inventory
- No manual effort
- No GCP cost
- No static credentials
- Full change history in Git

This setup scales well from small personal projects to professional environments.

---

## Possible extensions

- Summary sheet (counts per project / resource type)
- Compliance checks (public buckets, unlabeled resources)
- Notifications (Slack, n8n, email)
- Export to BigQuery (optional)

---

## Security notes

- Access is restricted per-repository
- No secrets are committed
- Service account is read-only
- Permissions are auditable and revocable

---

## License

MIT License

Copyright (c) 2026 Paolo Ronco

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
