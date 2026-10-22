from observations import observations
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
    enabled_data, enabled_error = execute(["services", "list", "--enabled", "--project", pid])
    enabled = {entry.get("config", {}).get("name") for entry in enabled_data} if isinstance(enabled_data, list) else None
    if enabled_error:
        output["errors"].append({"collector": "serviceDiscovery", **enabled_error})
    required = {"cloudRun": "run.googleapis.com", "firewall": "compute.googleapis.com", "buckets": "storage.googleapis.com", "serviceAccounts": "iam.googleapis.com", "iamPolicy": "cloudresourcemanager.googleapis.com"}
    for name, args in collectors.items():
        if enabled is not None and name in ("cloudRun", "firewall", "buckets") and required[name] not in enabled:
            output["services"][name] = {"status": "not_enabled"}
            continue
        data, error = execute(args)
        if error:
            output["errors"].append({"collector": name, **error})
            continue
        if name == "cloudRun":
            output["services"][name] = [{"name": r.get("metadata", {}).get("name") or r.get("name"), "location": r.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location") or r.get("location"), "ingress": r.get("metadata", {}).get("annotations", {}).get("run.googleapis.com/ingress") or r.get("ingress"), "serviceAccount": r.get("spec", {}).get("template", {}).get("spec", {}).get("serviceAccountName"), "minInstances": r.get("metadata", {}).get("annotations", {}).get("autoscaling.knative.dev/minScale"), "maxInstances": r.get("metadata", {}).get("annotations", {}).get("autoscaling.knative.dev/maxScale")} for r in data] if isinstance(data, list) else []
        elif name == "firewall":
            output["services"][name] = [{"name": r.get("name"), "direction": r.get("direction"), "disabled": r.get("disabled"), "priority": r.get("priority"), "network": r.get("network"), "sourceRanges": r.get("sourceRanges", []), "destinationRanges": r.get("destinationRanges", []), "allowed": [{"protocol": x.get("IPProtocol"), "ports": x.get("ports", [])} for x in r.get("allowed", [])], "denied": [{"protocol": x.get("IPProtocol"), "ports": x.get("ports", [])} for x in r.get("denied", [])]} for r in data] if isinstance(data, list) else []
        elif name == "buckets":
            output["services"][name] = [{"name": r.get("name"), "location": r.get("location"), "storageClass": r.get("storageClass"), "versioning": r.get("versioning", {}).get("enabled"), "uniformBucketLevelAccess": r.get("iamConfiguration", {}).get("uniformBucketLevelAccess", {}).get("enabled"), "publicAccessPrevention": r.get("iamConfiguration", {}).get("publicAccessPrevention"), "lifecycleRuleCount": len(r.get("lifecycle", {}).get("rule", []))} for r in data] if isinstance(data, list) else []
        elif name == "serviceAccounts":
            output["services"][name] = [{"email": r.get("email"), "disabled": r.get("disabled")} for r in data] if isinstance(data, list) else []
        elif name == "iamPolicy":
            output["services"][name] = {"bindingsCount": len(data.get("bindings", [])), "roles": sorted({b.get("role", "") for b in data.get("bindings", [])})}
    return output

def report(deep):
    lines = [
        f"# Deep analysis — {deep['projectId']}",
        "",
        "Read-only configuration metadata; findings are review prompts, not confirmed vulnerabilities.",
        "",
    ]
    findings = observations(deep)
    lines += ["## Security review", ""]
    if findings:
        for finding in findings:
            lines.append(f"- **Review** `{finding['resource']}`: {finding['detail']}")
    else:
        lines.append("No matching heuristic observations. This does not imply the project is secure.")
    lines.append("")
    for name, entries in sorted(deep["services"].items()):
        lines += [f"## {name}", ""]
        if isinstance(entries, list):
            lines.append(f"Discovered: **{len(entries)}**")
            if name == "firewall":
                lines += ["", "| Rule | Direction | Sources | Protocols / ports | Status |", "|---|---|---|---|---|"]
                for r in entries:
                    access = "; ".join(str(a.get("protocol", "")) + ":" + (",".join(a.get("ports", [])) or "all") for a in r.get("allowed", []))
                    vals = [r.get("name"), r.get("direction"), ", ".join(r.get("sourceRanges", [])), access, "disabled" if r.get("disabled") else "enabled"]
                    lines.append("| " + " | ".join(str(v or "—").replace("|", "\\|").replace("\\n", " ") for v in vals) + " |")
            else:
                for item in entries:
                    label = item.get("name") or item.get("email") or "unknown"
                    details = ", ".join(f"{k}: {v}" for k, v in item.items() if k not in ("name", "email") and v is not None and v != [] and v != "")
                    lines.append(f"- `{str(label).replace(chr(96), '')}`" + (f" — {details}" if details else ""))
        elif entries.get("status") == "not_enabled":
            lines.append("API not enabled in this project.")
        else:
            lines.append(f"IAM bindings: **{entries.get('bindingsCount', 0)}**")
            lines.append("Roles: " + ", ".join(f"`{r}`" for r in entries.get("roles", [])))
        lines.append("")
    if deep["errors"]:
        lines += ["## Collection limitations", ""]
        for error in deep["errors"]:
            lines.append(f"- `{error['collector']}`: {error['type']}")
    return "\n".join(lines) + "\n"
