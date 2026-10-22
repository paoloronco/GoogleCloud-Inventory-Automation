# Deep configuration v6 — validation plan

Adds **allowlisted metadata only**, not raw service objects:

- Cloud Run: name, location, ingress, service-account identity, optional scaling annotations.
- Firewall: name, direction, priority, network, source/destination ranges, allow/deny protocol and ports.
- Cloud Storage: bucket name, location, storage class, versioning, uniform bucket-level access, public access prevention, lifecycle rule count.

These fields are descriptive and do not establish effective exposure or compliance. The collector intentionally does not read bucket objects, service environment variables, secret values, service account keys, or source code. IAM policy reporting remains role-summary only.

## Test before deployment

```bash
PYTHONPATH=cloudrun python3 -m unittest discover -s cloudrun -p 'test_*.py' -v
python3 -m py_compile cloudrun/job.py cloudrun/deep.py
```

Build a new immutable image tag after passing tests. Run once with `DRY_RUN=true,DEEP_SCAN=true`, inspect `deepResults` and only then manually publish with `DRY_RUN=false,DEEP_SCAN=true`.

## Known limitations

- Some fields are unavailable in `gcloud ... list` output; missing fields remain omitted.
- Deep report changes may occur due to API serialization changes.
- Current Markdown is still a technical inventory, not a relationship graph.
- Broad predefined read-only IAM roles should eventually be replaced with least-privilege custom roles.
- No scheduler is created or modified by this PR.
