import unittest
from unittest.mock import patch
from deep import inspect_project, report

class DeepTests(unittest.TestCase):
    @patch("deep.execute")
    def test_partial_collection(self, execute):
        execute.side_effect = [([{"config": {"name": x}} for x in ("run.googleapis.com", "compute.googleapis.com", "storage.googleapis.com")], None), (None, {"type": "command_failed"}), ([], None), ([], None), ([], None), ({"bindings": [{"role": "roles/viewer"}]}, None)]
        data = inspect_project("test-project")
        self.assertEqual(len(data["errors"]), 1)
        self.assertIn("Collection limitations", report(data))
        self.assertIn("roles/viewer", report(data))

    @patch("deep.execute")
    def test_firewall_fields(self, execute):
        def fake_execute(args):
            command = tuple(args[:3])
            if command == ("services", "list", "--enabled"):
                return ([{"config": {"name": "compute.googleapis.com"}}], None)
            if command == ("compute", "firewall-rules", "list"):
                return ([{"name": "allow-ssh", "direction": "INGRESS",
                          "sourceRanges": ["0.0.0.0/0"],
                          "allowed": [{"IPProtocol": "tcp", "ports": ["22"]}]}], None)
            if command == ("iam", "service-accounts", "list"):
                return ([], None)
            if command == ("projects", "get-iam-policy", "test"):
                return ({"bindings": []}, None)
            self.fail(f"Unexpected collector call: {args}")

        execute.side_effect = fake_execute
        result = inspect_project("test")
        self.assertEqual(result["services"]["firewall"][0]["sourceRanges"], ["0.0.0.0/0"])
        self.assertIn("0.0.0.0/0", report(result))
        self.assertEqual(result["services"]["cloudRun"], {"status": "not_enabled"})
        self.assertEqual(result["services"]["buckets"], {"status": "not_enabled"})

if __name__ == "__main__":
    unittest.main()
