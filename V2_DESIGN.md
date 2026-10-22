# Google Cloud Inventory v2 (proposed)

This branch is a **non-production prototype**, not yet a replacement for the existing daily inventory.

## Architecture
- Two independent GitHub OIDC → Google Cloud WIF identities, one per access domain.
- Dynamic project discovery per identity (no static projects.txt).
- Cloud Asset Inventory resource search and enabled API enumeration.
- Weekly deep collection of IAM policy, firewall rules and Cloud Run services.
- Per-project JSON and per-identity status/error reports.
- GitHub Actions artifacts first; publishing into the private data repository requires a separately reviewed integration.

## Configuration required
Create repository secrets `GCP_WIF_PROVIDER_A`, `GCP_SERVICE_ACCOUNT_A`, `GCP_WIF_PROVIDER_B`, `GCP_SERVICE_ACCOUNT_B`.
Grant the GitHub OIDC principals impersonation via `roles/iam.workloadIdentityUser` on the respective service accounts, with a restricted repository/ref attribute condition.
Grant minimum read permissions for project discovery, Cloud Asset Inventory, Service Usage, IAM policy, firewall and Cloud Run enumeration at the appropriate scopes. Use custom roles where possible and test each scope separately. No service-account JSON keys.

## Security and limitations
Read-only, no secrets or payload extraction. Redaction is a defensive safeguard, not a guarantee: review collected metadata before external distribution. The prototype does not collect source code, bucket objects, Secret Manager values, or application files. IAM/firewall/Run coverage is intentionally partial; further collectors and normalization are needed. A failed collector marks the job failed rather than silently reporting a complete inventory.

## Rollout
1. Diagnose existing Actions failures and restore runner availability.
2. Configure both identities and verify project visibility.
3. Test manually, review output and missing permissions.
4. Add normalized cross-account merge, Markdown reports, diffs and private-repo publishing.
5. Replace legacy scheduling only after validation.
