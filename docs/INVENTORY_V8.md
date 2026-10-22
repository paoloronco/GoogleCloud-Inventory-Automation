# Inventory v8 — resource classification

The previous overview counted all Cloud Asset Inventory entries as "resources", including administrative and managed objects. The new reporting layer distinguishes known deployed workloads and data resources from configuration, system and unclassified assets. **The raw inventory JSON is unchanged.**

Classification is intentionally conservative and uses an explicit allowlist of Google Cloud asset types. Unknown types remain unclassified; they are never silently counted as deployed workloads. The "primary" count is not a complete inventory of every possible GCP service.

The report groups resource types and separates enabled APIs. The existing Deep Analysis reports remain independent and unchanged.

## Planned follow-up

- Add a versioned Excel workbook with filtered worksheets and consistent schemas.
- Migrate identity namespaces from `primary` / `secondary` to `paolo.ronco2000` / `paolo.ronco20` with a one-time, reviewed output-path migration; do not delete historical directories until new paths are verified.
- Expand the type taxonomy based on real asset distributions and validate against the six and eight existing projects.
- Improve Markdown deep reports without collecting secret values.

Run unit tests before building a new image. This PR does not change Cloud Run, IAM, Scheduler or the publisher's output path.
