# Inventory v8 — Excel and account paths

The collector now generates `accounts/<identity>/inventory.xlsx` alongside JSON and Markdown. Workbook tabs: Overview, Resources, Networking, IAM, Enabled APIs, Security Review and Raw Inventory. The workbook is produced from the same snapshot and optional deep metadata as the Markdown report.

**Path migration:** existing `INVENTORY_IDENTITY=primary` maps to `paolo.ronco2000`; `secondary` maps to `paolo.ronco20`. Both canonical names are accepted directly. Old folders remain untouched for audit and rollback; do not delete them until both new locations are verified. Because the output path changes, the first publication under each new identity has no previous snapshot and no initial CHANGES.md.

**Rollout:** run unit tests, build a new image tag, update the job with DRY_RUN=true, and test both identities independently with explicit PROJECT_SCOPE. Publish each only after validating the dry-run. Do not run concurrent publishing executions.

The Excel contains metadata only. It does not retrieve secret values, source code, bucket objects or complete IAM principals. Counts are indicative, and unclassified assets are not counted as known workloads. Scheduler remains disabled.
