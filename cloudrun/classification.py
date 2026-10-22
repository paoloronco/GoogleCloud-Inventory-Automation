"""Explicit taxonomy of Cloud Asset Inventory types. No inferred ownership."""
from collections import Counter

RULES = {
    "storage.googleapis.com/Bucket": ("Data & Storage", "primary"),
    "sqladmin.googleapis.com/Instance": ("Data & Storage", "primary"),
    "firestore.googleapis.com/Database": ("Data & Storage", "primary"),
    "bigquery.googleapis.com/Dataset": ("Data & Storage", "primary"),
    "compute.googleapis.com/Instance": ("Workloads", "primary"),
    "run.googleapis.com/Service": ("Workloads", "primary"),
    "run.googleapis.com/Job": ("Workloads", "primary"),
    "cloudfunctions.googleapis.com/CloudFunction": ("Workloads", "primary"),
    "cloudfunctions.googleapis.com/Function": ("Workloads", "primary"),
    "container.googleapis.com/Cluster": ("Workloads", "primary"),
    "aiplatform.googleapis.com/ReasoningEngine": ("Workloads", "primary"),
    "compute.googleapis.com/Network": ("Networking", "configuration"),
    "compute.googleapis.com/Subnetwork": ("Networking", "configuration"),
    "compute.googleapis.com/Firewall": ("Networking", "configuration"),
    "compute.googleapis.com/FirewallPolicy": ("Networking", "configuration"),
    "compute.googleapis.com/Route": ("Networking", "configuration"),
    "iam.googleapis.com/ServiceAccount": ("Identity & Security", "configuration"),
    "iam.googleapis.com/Role": ("Identity & Security", "configuration"),
    "iam.googleapis.com/WorkloadIdentityPool": ("Identity & Security", "configuration"),
    "iam.googleapis.com/WorkloadIdentityPoolProvider": ("Identity & Security", "configuration"),
    "secretmanager.googleapis.com/Secret": ("Identity & Security", "configuration"),
    "apikeys.googleapis.com/Key": ("Identity & Security", "configuration"),
    "recaptchaenterprise.googleapis.com/Key": ("Identity & Security", "configuration"),
    "artifactregistry.googleapis.com/Repository": ("Build & Artifacts", "configuration"),
    "pubsub.googleapis.com/Topic": ("Messaging & Events", "configuration"),
    "pubsub.googleapis.com/Subscription": ("Messaging & Events", "configuration"),
    "eventarc.googleapis.com/Trigger": ("Messaging & Events", "configuration"),
    "monitoring.googleapis.com/AlertPolicy": ("Observability", "configuration"),
    "monitoring.googleapis.com/NotificationChannel": ("Observability", "configuration"),
    "logging.googleapis.com/LogSink": ("Observability", "configuration"),
    "firebaserules.googleapis.com/Ruleset": ("Identity & Security", "configuration"),
    "firebaserules.googleapis.com/Release": ("Identity & Security", "configuration"),
    "identitytoolkit.googleapis.com/Config": ("Identity & Security", "configuration"),
    "identitytoolkit.googleapis.com/OauthIdpConfig": ("Identity & Security", "configuration"),
    "identitytoolkit.googleapis.com/DefaultSupportedIdpConfig": ("Identity & Security", "configuration"),
    "osconfig.googleapis.com/OSPolicyAssignment": ("Identity & Security", "configuration"),
    "storageinsights.googleapis.com/ReportConfig": ("Observability", "configuration"),
    "cloudquotas.googleapis.com/QuotaPreference": ("Project Metadata", "configuration"),
    "compute.googleapis.com/InstanceSettings": ("Project Metadata", "configuration"),
    "firebase.googleapis.com/FirebaseAppInfo": ("Project Metadata", "configuration"),
    "firebase.googleapis.com/FirebaseProject": ("Project Metadata", "configuration"),
    "cloudresourcemanager.googleapis.com/Project": ("Project Metadata", "configuration"),
    "cloudbilling.googleapis.com/ProjectBillingInfo": ("Project Metadata", "configuration"),
    "compute.googleapis.com/Project": ("Project Metadata", "configuration"),
    "discoveryengine.googleapis.com/Collection": ("Data & Storage", "configuration"),
    "dataplex.googleapis.com/EntryGroup": ("Data & Storage", "configuration"),
}
SYSTEM_TYPES = {
    "run.googleapis.com/Execution", "run.googleapis.com/Task",
    "run.googleapis.com/Revision", "cloudfunctions.googleapis.com/FunctionVersion",
    "artifactregistry.googleapis.com/DockerImage", "containerregistry.googleapis.com/Image",
    "iam.googleapis.com/ServiceAccountKey", "secretmanager.googleapis.com/SecretVersion",
    "logging.googleapis.com/LogBucket", "firestore.googleapis.com/Backup",
    "storageinsights.googleapis.com/ReportDetail",
}
def classify(resource):
    kind = resource.get("assetType") or ""
    if kind.startswith("serviceusage.googleapis.com/"):
        return {"category": "Enabled APIs", "layer": "api", "confidence": "explicit"}
    if kind in RULES:
        category, layer = RULES[kind]
        return {"category": category, "layer": layer, "confidence": "explicit"}
    if kind in SYSTEM_TYPES:
        return {"category": "Managed & System", "layer": "system", "confidence": "explicit"}
    if kind.endswith("/ServiceAgent"):
        return {"category": "Managed & System", "layer": "system", "confidence": "heuristic"}
    return {"category": "Other / Unclassified", "layer": "unclassified", "confidence": "unknown"}

def counts(resources):
    result = Counter(classify(r)["layer"] for r in resources)
    return {k: result.get(k, 0) for k in ("primary", "configuration", "system", "api", "unclassified")}

def logical_workloads(resources):
    """Conservative candidates, not guaranteed deduplication.

    Only collapse matching Cloud Function / Cloud Run names when the function's
    fully qualified parent and region match the service's project and region.
    """
    def parts(resource):
        name = resource.get("name") or ""
        location = (resource.get("location") or "").lower()
        project = None
        chunks = name.split("/")
        for key in ("projects",):
            if key in chunks:
                idx = chunks.index(key)
                if idx + 1 < len(chunks):
                    project = chunks[idx + 1]
        return project, location, chunks[-1]

    workloads = [r for r in resources if classify(r)["category"] == "Workloads"]
    functions = {parts(r) for r in workloads if r.get("assetType") in
                 ("cloudfunctions.googleapis.com/Function", "cloudfunctions.googleapis.com/CloudFunction")}
    collapsed = 0
    for r in workloads:
        if r.get("assetType") == "run.googleapis.com/Service" and parts(r) in functions:
            collapsed += 1
    return {"primaryEntries": len(workloads), "possibleDuplicates": collapsed,
            "estimatedDistinct": len(workloads) - collapsed}
