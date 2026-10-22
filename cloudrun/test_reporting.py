import unittest
from reporting import compare, normalized, project_report, changes_report, overview

class ReportingTests(unittest.TestCase):
    def test_diff(self):
        old = [{"projectId": "p", "resources": [{"name": "a", "assetType": "T", "location": "eu"}], "apis": [{"name": "x"}]}]
        new = [{"projectId": "p", "resources": [{"name": "a", "assetType": "T", "location": "us"}, {"name": "b", "assetType": "T"}], "apis": [{"name": "y"}]}]
        result = compare(old, new)["p"]
        self.assertEqual(result["added"], ["b"])
        self.assertEqual(result["modified"], ["a"])
        self.assertEqual(result["apisEnabled"], ["y"])
        self.assertEqual(result["apisDisabled"], ["x"])
    def test_transient_execution_ignored(self):
        old = [{"projectId": "p", "resources": [], "apis": []}]
        new = [{"projectId": "p", "resources": [{"name": "//run/execution/1", "assetType": "run.googleapis.com/Execution"}], "apis": []}]
        self.assertEqual(compare(old, new), {})
        self.assertIn("No material changes detected.", changes_report({}))

    def test_api_assets_not_double_counted(self):
        p = {"projectId": "sample", "resources": [
            {"name": "api-asset", "assetType": "serviceusage.googleapis.com/Service"},
            {"name": "unknown", "assetType": "example.googleapis.com/Unknown"},
            {"name": "bucket", "assetType": "storage.googleapis.com/Bucket"},
        ], "apis": [{"name": "example.googleapis.com"}]}
        summary = overview("account", [p])
        self.assertIn("| `sample` | 1 | 0 | 0 | 1 | 1 |", summary)
        report = project_report(p)
        self.assertIn("Other/unclassified: **1**", report)
        self.assertIn("API asset records: **1**", report)
        self.assertNotIn("## Enabled APIs (", report)

    def test_report(self):
        text = project_report({"projectId": "p", "resources": [], "apis": []})
        self.assertIn("Project: p", text)

if __name__ == "__main__":
    unittest.main()
