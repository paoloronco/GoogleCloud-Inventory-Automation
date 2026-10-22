import unittest
from classification import classify, counts, logical_workloads
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

    def test_observed_asset_types(self):
        cases = {
            "serviceusage.googleapis.com/Service": "api",
            "compute.googleapis.com/Route": "configuration",
            "dataplex.googleapis.com/EntryGroup": "configuration",
            "artifactregistry.googleapis.com/DockerImage": "system",
            "iam.googleapis.com/ServiceAccountKey": "system",
            "run.googleapis.com/Revision": "system",
            "run.googleapis.com/Job": "primary",
        }
        for asset_type, expected in cases.items():
            with self.subTest(asset_type=asset_type):
                self.assertEqual(classify({"assetType": asset_type})["layer"], expected)

    def test_dedup_requires_matching_project_and_region(self):
        resources = [
            {"assetType": "cloudfunctions.googleapis.com/Function", "name": "//cloudfunctions.googleapis.com/projects/demo/locations/europe-west3/functions/send", "location": "europe-west3"},
            {"assetType": "run.googleapis.com/Service", "name": "//run.googleapis.com/projects/demo/locations/europe-west3/services/send", "location": "europe-west3"},
            {"assetType": "run.googleapis.com/Service", "name": "//run.googleapis.com/projects/other/locations/europe-west3/services/send", "location": "europe-west3"},
        ]
        result = logical_workloads(resources)
        self.assertEqual(result["possibleDuplicates"], 1)
        self.assertEqual(result["estimatedDistinct"], 2)

if __name__ == "__main__":
    unittest.main()
