import unittest
from unittest.mock import patch
from deep import inspect_project, report

class DeepTests(unittest.TestCase):
    @patch("deep.execute")
    def test_partial_collection(self, execute):
        execute.side_effect = [(None, {"type": "command_failed"}), ([], None), ([], None), ([], None), ({"bindings": [{"role": "roles/viewer"}]}, None)]
        data = inspect_project("test-project")
        self.assertEqual(len(data["errors"]), 1)
        self.assertIn("Collection limitations", report(data))
        self.assertIn("roles/viewer", report(data))

if __name__ == "__main__":
    unittest.main()
