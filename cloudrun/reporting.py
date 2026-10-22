from classification import classify, counts
"""Deterministic inventory normalization, diff and Markdown reporting."""
import hashlib
import json
from collections import Counter

def is_transient(resource):
    return resource.get("assetType") in {"run.googleapis.com/Execution", "run.googleapis.com/Task"}

def normalized(projects):
    result = {}
    for project in projects:
        pid = project["projectId"]
        resources = {}
        for resource in project.get("resources", []):
            key = resource.get("name")
            if not key or is_transient(resource):
                continue
            resources[key] = {k: resource.get(k) for k in ("name", "assetType", "location", "state")}
        apis = sorted({a["name"] for a in project.get("apis", []) if a.get("name")})
        result[pid] = {"resources": resources, "apis": apis}
    return result

def compare(previous, current):
    old = normalized(previous)
    new = normalized(current)
    changes = {}
    for pid in sorted(set(old) | set(new)):
        before = old.get(pid, {"resources": {}, "apis": []})
        after = new.get(pid, {"resources": {}, "apis": []})
        a, b = before["resources"], after["resources"]
        delta = {
            "added": sorted(set(b) - set(a)),
            "removed": sorted(set(a) - set(b)),
            "modified": sorted(k for k in set(a) & set(b) if a[k] != b[k]),
            "apisEnabled": sorted(set(after["apis"]) - set(before["apis"])),
            "apisDisabled": sorted(set(before["apis"]) - set(after["apis"])),
        }
        if any(delta.values()):
            changes[pid] = delta
    return changes

def overview(identity, projects):
    lines = ["# Google Cloud Inventory", "", f"Account: `{identity}`", "",
             "Primary resources are an indicative subset of deployed workloads and data stores; other assets remain available in the JSON.",
             "", "| Project | Primary resources | Configuration | System | Other | Enabled APIs |",
             "|---|---:|---:|---:|---:|---:|"]
    for p in sorted(projects, key=lambda x: x["projectId"]):
        c = counts(p.get("resources", []))
        lines.append(f"| `{p['projectId']}` | {c['primary']} | {c['configuration']} | {c['system']} | {c['unclassified'] + c['api']} | {len(p.get('apis', []))} |")
    return "\n".join(lines) + "\n"

def project_report(project):
    pid = project["projectId"]
    resources = project.get("resources", [])
    c = counts(resources)
    lines = [f"# Project: {pid}", "", "## At a glance", "",
             f"- Primary resources: **{c['primary']}** (known workload and data types only)",
             f"- Configuration assets: **{c['configuration']}**",
             f"- Managed/system assets: **{c['system']}**",
             f"- Other/unclassified: **{c['unclassified'] + c['api']}**",
             f"- Enabled APIs: **{len(project.get('apis', []))}** (not deployments)", "",
             "Counts are based on Cloud Asset Inventory types. Unknown types are not assumed to be user deployments.",
             ""]
    groups = [("Workloads", "Workloads"), ("Data & Storage", "Data & Storage"),
              ("Networking", "Networking"), ("Identity & Security", "Identity & Security"),
              ("Managed & System", "Managed & System"), ("Other / Unclassified", "Other / Unclassified"),
              ("Enabled APIs", "Enabled APIs")]
    for title, category in groups:
        items = sorted((r for r in resources if classify(r)["category"] == category), key=lambda x: x.get("name") or "")
        if not items:
            continue
        lines += [f"## {title} ({len(items)})", "", "| Resource | Asset type | Location |", "|---|---|---|"]
        for r in items:
            name = (r.get("name") or "").rsplit("/", 1)[-1]
            vals = [name, r.get("assetType") or "", r.get("location") or ""]
            lines.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in vals) + " |")
        lines.append("")
    lines += ["## Enabled services", "", "These are enabled APIs, not deployed resources.", ""]
    for api in sorted(project.get("apis", []), key=lambda x: x.get("name") or ""):
        lines.append(f"- `{api.get('name', '')}`")
    return "\n".join(lines) + "\n"

def changes_report(changes):
    lines = ["# Inventory changes", "", "Comparison with previous successfully published snapshot.", ""]
    if not changes:
        lines += ["No material changes detected.", ""]
    for pid, sections in sorted(changes.items()):
        lines += [f"## {pid}", ""]
        for key, values in sections.items():
            if not values:
                continue
            lines.append(f"### {key} ({len(values)})")
            lines += [f"- `{v}`" for v in values]
            lines.append("")
    return "\n".join(lines) + "\n"
