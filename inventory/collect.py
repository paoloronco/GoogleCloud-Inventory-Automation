#!/usr/bin/env python3
"""Read-only Google Cloud inventory. Requires gcloud authenticated through WIF."""
import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def gcloud(*args):
    p = subprocess.run(["gcloud", *args, "--format=json"], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"gcloud {' '.join(args)}: {p.stderr.strip()}")
    return json.loads(p.stdout or "[]")

def safe(value):
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items() if not any(s in k.lower() for s in ("secret", "password", "token", "private_key", "credential", "userdata", "user_data", "env"))}
    if isinstance(value, list):
        return [safe(v) for v in value]
    return value

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", required=True)
    ap.add_argument("--out", default="output")
    ap.add_argument("--deep", action="store_true")
    args = ap.parse_args()
    root = Path(args.out)
    stamp = datetime.now(timezone.utc).isoformat()
    failures = []
    projects = gcloud("projects", "list")
    summary = []
    for project in projects:
        pid = project["projectId"]
        entry = {"projectId": pid, "projectNumber": project.get("projectNumber"), "name": project.get("name"), "lifecycleState": project.get("lifecycleState"), "parent": project.get("parent")}
        try:
            resources = gcloud("asset", "search-all-resources", f"--scope=projects/{pid}")
            entry["resources"] = len(resources)
            write(root / "projects" / pid / "resources.json", safe(resources))
        except Exception as exc:
            failures.append({"project": pid, "stage": "resources", "error": str(exc)})
            entry["resources"] = None
        try:
            apis = gcloud("services", "list", "--enabled", "--project", pid)
            entry["enabledApis"] = len(apis)
            write(root / "projects" / pid / "apis.json", safe(apis))
        except Exception as exc:
            failures.append({"project": pid, "stage": "apis", "error": str(exc)})
            entry["enabledApis"] = None
        if args.deep:
            for label, cmd in {
                "iam-policy": ("projects", "get-iam-policy", pid),
                "firewall-rules": ("compute", "firewall-rules", "list", "--project", pid),
                "cloud-run": ("run", "services", "list", "--platform=managed", "--project", pid),
            }.items():
                try:
                    write(root / "projects" / pid / f"{label}.json", safe(gcloud(*cmd)))
                except Exception as exc:
                    failures.append({"project": pid, "stage": label, "error": str(exc)})
        summary.append(entry)
    write(root / "accounts" / f"{args.identity}.json", {"identity": args.identity, "scannedAt": stamp, "projects": summary, "failures": failures})
    print(f"identity={args.identity} projects={len(summary)} errors={len(failures)}")
    if failures:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
