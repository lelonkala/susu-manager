import unittest

from susu.errors import SusuError
from susu.group import Group


def make_group():
    g = Group(5000)
    for n in ["Ama", "Kofi", "Esi"]:
        g.add_member(n)
    return g


class ContributionTests(unittest.TestCase):
    def test_partial_payment_reduces_balance(self):
        g = make_group()
        self.assertEqual(g.record_contribution("Esi", 3000), 2000)
        self.assertEqual(g.owed("Esi"), 2000)
        self.assertEqual(g.record_contribution("Esi", 2000), 0)

    def test_unknown_member_rejected(self):
        with self.assertRaises(SusuError):
            make_group().record_contribution("Yaw", 100)

    def test_zero_and_negative_rejected(self):
        g = make_group()
        for bad in (0, -1):
            with self.assertRaises(SusuError):
                g.record_contribution("Ama", bad)

    def test_overpayment_rejected_including_after_partial(self):
        g = make_group()
        with self.assertRaises(SusuError):
            g.record_contribution("Ama", 5001)
        g.record_contribution("Ama", 4000)
        with self.assertRaises(SusuError):
            g.record_contribution("Ama", 1001)
        self.assertEqual(g.owed("Ama"), 1000)  # failed attempts changed nothing

    def test_wrong_week_rejected(self):
        with self.assertRaises(SusuError):
            make_group().record_contribution("Ama", 100, week=2)

    def test_cannot_add_member_after_contributions_start(self):
        g = make_group()
        g.record_contribution("Ama", 100)
        with self.assertRaises(SusuError):
            g.add_member("Yaw")
