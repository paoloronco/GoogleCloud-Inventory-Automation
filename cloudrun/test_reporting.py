import unittest
from reporting import compare, normalized, project_report, changes_report

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

    def test_report(self):
        text = project_report({"projectId": "p", "resources": [], "apis": []})
        self.assertIn("Project: p", text)

if __name__ == "__main__":
    unittest.main()
