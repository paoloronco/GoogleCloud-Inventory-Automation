# Inventory reporting v4 — implementation notes

This change adds deterministic per-project Markdown reports and compares successive successful snapshots before publishing.

## Test locally
```bash
PYTHONPATH=cloudrun python3 -m unittest discover -s cloudrun -p 'test_*.py'
python3 -m py_compile cloudrun/job.py cloudrun/reporting.py
```

## Safety
- Existing Cloud Run job remains on its previous container image.
- `DRY_RUN=true` remains the default and does not contact GitHub.
- Publishing requires `DRY_RUN=false`, a repository-scoped token, and explicitly approved project IDs.
- No scheduler changes.
- The current deep collector only records counts, not detailed configuration documentation.
- GitHub Contents API writes are sequential and not transactional; a later error may leave some updated files.
- Diff is generated only when a previous snapshot exists; the initial publication establishes a baseline.
- API/resource metadata is not a complete security audit.

## Next work
Add read-only deep collectors with explicit allowlists, redaction, permission-failure reporting, and isolated tests before enabling weekly scans.
