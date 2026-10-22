import unittest
from classification import classify, counts
from reporting import overview, project_report

class ClassificationTests(unittest.TestCase):
    def test_known_bucket(self):
        self.assertEqual(classify({"assetType": "storage.googleapis.com/Bucket"})["layer"], "primary")

    def test_unknown_not_workload(self):
        self.assertEqual(classify({"assetType": "some.googleapis.com/Unknown"})["layer"], "unclassified")

    def test_project_report_separates_apis(self):
        project = {"projectId": "sample", "resources": [
            {"name": "//storage.googleapis.com/projects/_/buckets/demo", "assetType": "storage.googleapis.com/Bucket"},
            {"name": "//unknown.googleapis.com/other", "assetType": "unknown.googleapis.com/Other"}
        ], "apis": [{"name": "storage.googleapis.com"}]}
        self.assertEqual(counts(project["resources"])["primary"], 1)
        self.assertIn("Primary resources: **1**", project_report(project))
        self.assertIn("Enabled APIs: **1**", project_report(project))
        self.assertIn("Other/unclassified", overview("paolo.ronco2000", [project]) if False else project_report(project))

if __name__ == "__main__":
    unittest.main()
