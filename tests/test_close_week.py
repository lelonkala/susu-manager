import unittest

from susu.errors import SusuError
from susu.group import Group


def make_group():
    g = Group(5000)
    for n in ["Ama", "Kofi", "Esi"]:
        g.add_member(n)
    return g


class CloseWeekTests(unittest.TestCase):
    def test_week_cannot_close_when_someone_owes(self):
        g = make_group()
        g.record_contribution("Ama", 5000)
        g.record_contribution("Kofi", 5000)
        g.record_contribution("Esi", 3000)
        result = g.close_week()
        self.assertFalse(result.closed)
        self.assertEqual(result.owing, {"Esi": 2000})
        self.assertEqual(g.current_week, 1)
        self.assertEqual(g.payouts, [])

    def test_spec_example_end_to_end(self):
        g = make_group()
        g.record_contribution("Ama", 5000)
        g.record_contribution("Kofi", 5000)
        g.record_contribution("Esi", 3000)
        self.assertFalse(g.close_week().closed)
        g.record_contribution("Esi", 2000)
        result = g.close_week()
        self.assertTrue(result.closed)
        self.assertEqual((result.payout.member, result.payout.amount), ("Ama", 15000))
        self.assertEqual(g.current_week, 2)
        self.assertEqual(g.report().next_recipient, "Kofi")
        self.assertEqual(g.owed("Ama"), 5000)  # balances reset for new week

    def test_nobody_paid_means_everyone_owes(self):
        g = make_group()
        self.assertEqual(g.close_week().owing, {"Ama": 5000, "Kofi": 5000, "Esi": 5000})

    def test_full_cycle_pays_each_member_once_in_join_order(self):
        g = make_group()
        for _ in range(3):
            for m in g.members:
                g.record_contribution(m, 5000)
            self.assertTrue(g.close_week().closed)
        self.assertEqual([p.member for p in g.payouts], ["Ama", "Kofi", "Esi"])
        self.assertTrue(g.report().finished)
        with self.assertRaises(SusuError):
            g.record_contribution("Ama", 100)
        with self.assertRaises(SusuError):
            g.close_week()

    def test_cannot_close_with_no_members(self):
        with self.assertRaises(SusuError):
            Group(5000).close_week()

    def test_report_lists_paid_and_owing(self):
        g = make_group()
        g.record_contribution("Ama", 5000)
        g.record_contribution("Kofi", 1050)
        r = g.report()
        self.assertEqual(r.paid_in_full, ["Ama"])
        self.assertEqual(r.owing, {"Kofi": 3950, "Esi": 5000})
