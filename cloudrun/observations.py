"""Heuristic, non-authoritative security observations from collected metadata."""
def observations(deep):
    findings = []
    for rule in deep.get("services", {}).get("firewall", []):
        if not isinstance(rule, dict) or rule.get("disabled") is True or rule.get("direction") != "INGRESS":
            continue
        if "0.0.0.0/0" not in rule.get("sourceRanges", []):
            continue
        for allow in rule.get("allowed", []):
            proto = str(allow.get("protocol", "")).lower()
            ports = allow.get("ports", [])
            if proto == "all" or (proto in ("tcp", "6") and (not ports or any(p in ("22", "3389", "0-65535") for p in ports))):
                findings.append({"category": "firewall-review", "resource": rule.get("name"), "detail": "Ingress allows broad IPv4 sources with all protocols or administrative ports; effective exposure requires target and policy validation."})
                break
    return sorted(findings, key=lambda f: (f["category"], f["resource"] or ""))
