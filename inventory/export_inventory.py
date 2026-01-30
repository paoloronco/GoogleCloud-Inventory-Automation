import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
PROJECTS_FILE = ROOT / "projects.txt"

# Asset types utili (puoi aggiungerne altri quando vuoi)
ASSET_TYPES = [
    "compute.googleapis.com/Instance",
    "compute.googleapis.com/Disk",
    "storage.googleapis.com/Bucket",
    "run.googleapis.com/Service",
    "artifactregistry.googleapis.com/Repository",
    "iam.googleapis.com/ServiceAccount",
    "sqladmin.googleapis.com/Instance",
]

def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True)

def gcloud_json(args: list[str]) -> list | dict:
    out = run(["gcloud", *args, "--format=json"])
    if out.strip() == "":
        return []
    return json.loads(out)

def load_projects() -> list[str]:
    return [line.strip() for line in PROJECTS_FILE.read_text().splitlines() if line.strip() and not line.strip().startswith("#")]

def search_resources(project_id: str) -> list[dict]:
    asset_types = ",".join(ASSET_TYPES)
    return gcloud_json([
        "asset", "search-all-resources",
        f"--scope=projects/{project_id}",
        f"--asset-types={asset_types}",
        "--order-by=updateTime desc",
    ])
    
def enabled_apis(project_id: str) -> list[dict]:
    return gcloud_json(["services", "list", "--enabled", "--project", project_id])

def main():
    projects = load_projects()
    ts = datetime.now(timezone.utc).isoformat()

    res_rows = []
    api_rows = []
    proj_rows = []

    for pid in projects:
        proj_rows.append({"timestamp_utc": ts, "projectId": pid})

        # Resources
        resources = search_resources(pid)
        for r in resources:
            res_rows.append({
                "timestamp_utc": ts,
                "projectId": pid,
                "assetType": r.get("assetType"),
                "name": r.get("name"),
                "displayName": r.get("displayName"),
                "location": r.get("location"),
                "state": r.get("state"),
                "labels": json.dumps(r.get("labels", {}), ensure_ascii=False),
                "createTime": r.get("createTime"),
                "updateTime": r.get("updateTime"),
            })

        # Enabled APIs
        services = enabled_apis(pid)
        for s in services:
            cfg = s.get("config", {})
            api_rows.append({
                "timestamp_utc": ts,
                "projectId": pid,
                "serviceName": cfg.get("name"),
                "title": cfg.get("title"),
            })

    df_proj = pd.DataFrame(proj_rows)
    df_res = pd.DataFrame(res_rows)
    df_api = pd.DataFrame(api_rows)

    # CSV
    df_proj.to_csv("inventory_projects.csv", index=False)
    df_res.to_csv("inventory_resources.csv", index=False)
    df_api.to_csv("inventory_apis.csv", index=False)

    # Excel
    with pd.ExcelWriter("inventory.xlsx", engine="openpyxl") as w:
        df_proj.to_excel(w, sheet_name="Projects", index=False)
        df_res.to_excel(w, sheet_name="Resources", index=False)
        df_api.to_excel(w, sheet_name="Enabled_APIs", index=False)

if __name__ == "__main__":
    main()
