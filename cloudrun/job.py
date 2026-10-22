from deep import inspect_project, report as deep_report
from reporting import compare, overview, project_report, changes_report
"""Cloud Run entrypoint: collect inventory, build Markdown, publish to GitHub."""
import base64
import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from google.auth import default
from google.auth.transport.requests import Request

def access_token():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token

def github(path, method="GET", data=None):
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and method == "GET":
            return None
        raise RuntimeError(f"GitHub API {exc.code} for {path}") from exc

def publish(path, text):
    old = github(path)
    if old:
        existing = base64.b64decode(old["content"]).decode()
        if existing == text:
            return False
    payload = {"message": f"inventory: update {path}", "content": base64.b64encode(text.encode()).decode(), "branch": os.getenv("GITHUB_BRANCH", "master")}
    if old:
        payload["sha"] = old["sha"]
    github(path, "PUT", payload)
    return True

def main():
    identity = os.getenv("INVENTORY_IDENTITY", "primary")
    scope = os.getenv("PROJECT_SCOPE", "").strip()
    if not scope:
        raise RuntimeError("PROJECT_SCOPE is required: comma-separated project IDs. Explicit allowlist prevents accidental cross-account enumeration.")
    projects = [p.strip() for p in scope.split(",") if p.strip()]
    deep = os.getenv("DEEP_SCAN", "false").lower() == "true"
    dry_run = os.getenv("DRY_RUN", "true").strip().lower() in ("1", "true", "yes")
    stamp = datetime.now(timezone.utc).isoformat()
    records = []
    failures = []
    for pid in projects:
        project = {"projectId": pid}
        for kind, args in [
            ("resources", ["asset", "search-all-resources", f"--scope=projects/{pid}"]),
            ("apis", ["services", "list", "--enabled", "--project", pid]),
        ] + ([("iam", ["projects", "get-iam-policy", pid]), ("firewall", ["compute", "firewall-rules", "list", "--project", pid]), ("run", ["run", "services", "list", "--project", pid])] if deep else []):
            cmd = ["gcloud", *args, "--format=json"]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode:
                failures.append({"project": pid, "collector": kind, "error": proc.stderr[-500:]})
                continue
            try:
                data = json.loads(proc.stdout or "[]")
            except json.JSONDecodeError:
                failures.append({"project": pid, "collector": kind, "error": "invalid JSON"})
                continue
            # Metadata only. Never store service definitions or IAM bindings containing unexpected secrets without review.
            if kind in ("resources", "apis"):
                if kind == "resources":
                    data = [{"name": r.get("name"), "assetType": r.get("assetType"), "location": r.get("location"), "state": r.get("state")} for r in data]
                else:
                    data = [{"name": r.get("config", {}).get("name"), "title": r.get("config", {}).get("title")} for r in data]
                project[kind] = data
            else:
                project[kind + "Count"] = len(data) if isinstance(data, list) else len(data.get("bindings", []))
        records.append(project)
    if failures:
        print(json.dumps({"status": "incomplete", "failures": failures}), flush=True)
        raise SystemExit(2)
    snapshot = {"identity": identity, "scannedAt": stamp, "projects": records, "deep": deep}
    # Canonical content excludes scan timestamp to avoid commits without material changes.
    canonical = json.dumps({"identity": identity, "projects": records, "deep": deep}, sort_keys=True, indent=2) + "\n"
    summary_md = overview(identity, records)
    prefix = f"accounts/{identity}"
    deep_results = [inspect_project(pid) for pid in projects] if deep else []
    if dry_run:
        print(json.dumps({"deepResults": [{"projectId": d["projectId"], "sections": list(d["services"]), "errors": d["errors"]} for d in deep_results]}), flush=True) if deep else None
        print(json.dumps({"status": "dry-run", "identity": identity, "projects": [{"projectId": r["projectId"], "resources": len(r.get("resources", [])), "enabledApis": len(r.get("apis", []))} for r in records], "deep": deep}), flush=True)
        return
    previous = github(f"{prefix}/inventory.json")
    old_projects = []
    if previous:
        old_projects = json.loads(base64.b64decode(previous["content"]).decode()).get("projects", [])
    publish(f"{prefix}/inventory.json", canonical)
    publish(f"{prefix}/README.md", summary_md)
    for item in records:
        publish(f"{prefix}/projects/{item['projectId']}.md", project_report(item))
    if previous:
        publish(f"{prefix}/CHANGES.md", changes_report(compare(old_projects, records)))
    for d in deep_results:
        publish(f"{prefix}/deep/{d['projectId']}.md", deep_report(d))
    print(json.dumps({"status": "ok", "identity": identity, "projects": len(records), "deep": deep, "timestamp": stamp}))

if __name__ == "__main__":
    main()
