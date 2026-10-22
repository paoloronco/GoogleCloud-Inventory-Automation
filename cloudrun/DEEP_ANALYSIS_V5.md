# Deep analysis v5 — rollout

This collector deliberately captures **safe metadata summaries only**. It does not retrieve secret values, bucket objects, source code, environment variables, service account keys, or full IAM principal lists.

Collectors: Cloud Run service names, firewall names/directions, bucket names/locations/storage classes, service account identifiers, IAM role names and binding counts.

Errors are recorded per collector and published in the deep report, so unsupported or disabled services are visible.

## Testing
```bash
PYTHONPATH=cloudrun python3 -m unittest discover -s cloudrun -p 'test_*.py' -v
```

## Rollout
1. Merge and build a new image tag; do not overwrite v3.
2. Manually test with `DRY_RUN=true,DEEP_SCAN=true` and inspect structured logs for permissions.
3. Grant narrowly scoped additional read permissions where needed; avoid blanket viewer/editor roles.
4. Publish only after reviewing the metadata and error handling.
5. Leave scheduler disabled until explicit approval.

This is an initial deep-inspection pass, **not** a full architecture reconstruction or security assessment.
