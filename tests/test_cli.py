import unittest

from susu.cli import Shell


class CliTests(unittest.TestCase):
    def test_spec_example_through_the_shell(self):
        s = Shell()
        s.execute("new 50.00")
        for n in ("Ama", "Kofi", "Esi"):
            s.execute(f"add {n}")
        s.execute("pay Ama 50")
        s.execute("pay Kofi 50")
        s.execute("pay Esi 30")
        self.assertIn("Esi owes GHS 20.00", s.execute("close"))
        s.execute("pay Esi 20")
        self.assertIn("Ama receives GHS 150.00", s.execute("close"))
        self.assertIn("Next recipient: Kofi", s.execute("report"))

    def test_errors_are_reported_not_raised(self):
        s = Shell()
        self.assertIn("no group", s.execute("report"))
        s.execute("new 50")
        s.execute("add Ama")
        self.assertIn("Error", s.execute("pay Ama 50.001"))
        self.assertIn("Error", s.execute("pay Ama 51"))
        self.assertIn("Error", s.execute("pay Yaw 5"))
