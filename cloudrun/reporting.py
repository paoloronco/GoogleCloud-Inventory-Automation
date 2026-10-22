"""Deterministic inventory normalization, diff and Markdown reporting."""
import hashlib
import json
from collections import Counter

def normalized(projects):
    result = {}
    for project in projects:
        pid = project["projectId"]
        resources = {}
        for resource in project.get("resources", []):
            key = resource.get("name")
            if not key:
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
        changes[pid] = {
            "added": sorted(set(b) - set(a)),
            "removed": sorted(set(a) - set(b)),
            "modified": sorted(k for k in set(a) & set(b) if a[k] != b[k]),
            "apisEnabled": sorted(set(after["apis"]) - set(before["apis"])),
            "apisDisabled": sorted(set(before["apis"]) - set(after["apis"])),
        }
    return changes

def overview(identity, projects):
    lines = ["# Google Cloud Inventory", "", f"Identity: `{identity}`", "", "| Project | Resources | Enabled APIs |", "|---|---:|---:|"]
    for p in sorted(projects, key=lambda x: x["projectId"]):
        lines.append(f"| `{p['projectId']}` | {len(p.get('resources', []))} | {len(p.get('apis', []))} |")
    return "\n".join(lines) + "\n"

def project_report(project):
    pid = project["projectId"]
    counts = Counter(r.get("assetType") or "unknown" for r in project.get("resources", []))
    lines = [f"# Project: {pid}", "", f"Resources: **{len(project.get('resources', []))}**", f"Enabled APIs: **{len(project.get('apis', []))}**", "", "## Resources by type", "", "| Type | Count |", "|---|---:|"]
    for kind, count in sorted(counts.items()):
        lines.append(f"| `{kind}` | {count} |")
    lines += ["", "## Resource details", "", "| Name | Type | Location | State |", "|---|---|---|---|"]
    for r in sorted(project.get("resources", []), key=lambda x: x.get("name") or ""):
        vals = [str(r.get(k) or "").replace("|", "\\|").replace("\n", " ") for k in ("name", "assetType", "location", "state")]
        lines.append("| " + " | ".join(f"`{v}`" for v in vals) + " |")
    lines += ["", "## Enabled APIs", ""]
    for api in sorted(project.get("apis", []), key=lambda x: x.get("name") or ""):
        lines.append(f"- `{api.get('name', '')}`")
    return "\n".join(lines) + "\n"

def changes_report(changes):
    lines = ["# Inventory changes", "", "Comparison with previous successfully published snapshot.", ""]
    for pid, sections in sorted(changes.items()):
        lines += [f"## {pid}", ""]
        for key, values in sections.items():
            lines.append(f"### {key} ({len(values)})")
            lines += [f"- `{v}`" for v in values] or ["- None"]
            lines.append("")
    return "\n".join(lines) + "\n"
