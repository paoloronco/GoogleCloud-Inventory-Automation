import unittest
from observations import observations
from deep import report

class ObservationTests(unittest.TestCase):
    def test_broad_ssh_review(self):
        data = {"projectId": "p", "services": {"firewall": [{"name": "ssh", "direction": "INGRESS", "disabled": False, "sourceRanges": ["0.0.0.0/0"], "allowed": [{"protocol": "tcp", "ports": ["22"]}]}]}, "errors": []}
        self.assertEqual(len(observations(data)), 1)
        self.assertIn("Security review", report(data))
        self.assertIn("| Rule | Direction |", report(data))

    def test_disabled_rule_not_flagged(self):
        data = {"services": {"firewall": [{"name": "ssh", "direction": "INGRESS", "disabled": True, "sourceRanges": ["0.0.0.0/0"], "allowed": [{"protocol": "tcp", "ports": ["22"]}]}]}}
        self.assertEqual(observations(data), [])

if __name__ == "__main__":
    unittest.main()
