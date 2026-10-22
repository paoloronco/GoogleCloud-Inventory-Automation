"""Conservative, read-only deep inspection. No secrets or full IAM policies are exported."""
import json
import subprocess

def execute(args):
    result = subprocess.run(["gcloud", *args, "--format=json"], capture_output=True, text=True, timeout=90)
    if result.returncode:
        return None, {"type": "command_failed", "command": args[:3], "message": result.stderr[-300:]}
    try:
        return json.loads(result.stdout or "[]"), None
    except ValueError:
        return None, {"type": "invalid_json", "command": args[:3]}

def inspect_project(pid):
    output = {"projectId": pid, "services": {}, "errors": []}
    collectors = {
        "cloudRun": ["run", "services", "list", "--project", pid],
        "firewall": ["compute", "firewall-rules", "list", "--project", pid],
        "buckets": ["storage", "buckets", "list", "--project", pid],
        "serviceAccounts": ["iam", "service-accounts", "list", "--project", pid],
        "iamPolicy": ["projects", "get-iam-policy", pid],
    }
    for name, args in collectors.items():
        data, error = execute(args)
        if error:
            output["errors"].append({"collector": name, **error})
            continue
        if name == "cloudRun":
            output["services"][name] = [{"name": r.get("metadata", {}).get("name") or r.get("name"), "location": r.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location")} for r in data] if isinstance(data, list) else []
        elif name == "firewall":
            output["services"][name] = [{"name": r.get("name"), "direction": r.get("direction"), "disabled": r.get("disabled")} for r in data] if isinstance(data, list) else []
        elif name == "buckets":
            output["services"][name] = [{"name": r.get("name"), "location": r.get("location"), "storageClass": r.get("storageClass")} for r in data] if isinstance(data, list) else []
        elif name == "serviceAccounts":
            output["services"][name] = [{"email": r.get("email"), "disabled": r.get("disabled")} for r in data] if isinstance(data, list) else []
        elif name == "iamPolicy":
            output["services"][name] = {"bindingsCount": len(data.get("bindings", [])), "roles": sorted({b.get("role", "") for b in data.get("bindings", [])})}
    return output

def report(deep):
    lines = [f"# Deep analysis — {deep['projectId']}", "", "Read-only configuration metadata. Missing permissions are reported, not silently ignored.", ""]
    for name, entries in sorted(deep["services"].items()):
        lines += [f"## {name}", ""]
        if isinstance(entries, list):
            lines.append(f"Discovered: **{len(entries)}**")
            for item in entries:
                label = item.get("name") or item.get("email") or "unknown"
                lines.append(f"- `{str(label).replace(chr(96), '')}`")
        else:
            lines.append(f"IAM bindings: **{entries.get('bindingsCount', 0)}**")
            lines.append("Roles: " + ", ".join(f"`{r}`" for r in entries.get("roles", [])))
        lines.append("")
    if deep["errors"]:
        lines += ["## Collection limitations", ""]
        for error in deep["errors"]:
            lines.append(f"- `{error['collector']}`: {error['type']}")
    return "\n".join(lines) + "\n"
