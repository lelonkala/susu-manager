import unittest

from susu.errors import SusuError
from susu.group import Group


class MemberTests(unittest.TestCase):
    def test_add_members_keeps_join_order(self):
        g = Group(5000)
        for n in ["Ama", "Kofi", "Esi"]:
            g.add_member(n)
        self.assertEqual(g.members, ["Ama", "Kofi", "Esi"])

    def test_duplicate_member_rejected_case_insensitively(self):
        g = Group(5000)
        g.add_member("Ama")
        with self.assertRaises(SusuError):
            g.add_member(" ama ")

    def test_weekly_amount_must_be_positive(self):
        for bad in (0, -100):
            with self.assertRaises(SusuError):
                Group(bad)
