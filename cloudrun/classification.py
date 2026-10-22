"""Conservative resource taxonomy; raw Cloud Asset Inventory data is preserved."""
from collections import Counter

RULES = {
    "storage.googleapis.com/Bucket": ("Data & Storage", "primary"),
    "sqladmin.googleapis.com/Instance": ("Data & Storage", "primary"),
    "firestore.googleapis.com/Database": ("Data & Storage", "primary"),
    "bigquery.googleapis.com/Dataset": ("Data & Storage", "primary"),
    "compute.googleapis.com/Instance": ("Workloads", "primary"),
    "run.googleapis.com/Service": ("Workloads", "primary"),
    "cloudfunctions.googleapis.com/CloudFunction": ("Workloads", "primary"),
    "cloudfunctions.googleapis.com/Function": ("Workloads", "primary"),
    "container.googleapis.com/Cluster": ("Workloads", "primary"),
    "compute.googleapis.com/Network": ("Networking", "configuration"),
    "compute.googleapis.com/Subnetwork": ("Networking", "configuration"),
    "compute.googleapis.com/Firewall": ("Networking", "configuration"),
    "iam.googleapis.com/ServiceAccount": ("Identity & Security", "configuration"),
}
SYSTEM_TYPES = {
    "run.googleapis.com/Execution", "run.googleapis.com/Task",
    "run.googleapis.com/Revision", "cloudfunctions.googleapis.com/FunctionVersion",
}
def classify(resource):
    kind = resource.get("assetType") or ""
    if kind in RULES:
        category, layer = RULES[kind]
        return {"category": category, "layer": layer, "confidence": "explicit"}
    if kind in SYSTEM_TYPES or kind.endswith("/ServiceAgent"):
        return {"category": "Managed & System", "layer": "system", "confidence": "heuristic"}
    if kind.startswith("serviceusage.googleapis.com/"):
        return {"category": "Enabled APIs", "layer": "api", "confidence": "explicit"}
    return {"category": "Other / Unclassified", "layer": "unclassified", "confidence": "unknown"}

def counts(resources):
    result = Counter(classify(r)["layer"] for r in resources)
    return {k: result.get(k, 0) for k in ("primary", "configuration", "system", "api", "unclassified")}
