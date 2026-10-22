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
        execute.side_effect = [([{"config": {"name": "compute.googleapis.com"}}], None), ([], None), ([{"name": "allow-ssh", "direction": "INGRESS", "sourceRanges": ["0.0.0.0/0"], "allowed": [{"IPProtocol": "tcp", "ports": ["22"]}]}], None), ([], None), ([], None)]
        result = inspect_project("test")
        self.assertEqual(result["services"]["firewall"][0]["sourceRanges"], ["0.0.0.0/0"])
        self.assertIn("0.0.0.0/0", report(result))

if __name__ == "__main__":
    unittest.main()
