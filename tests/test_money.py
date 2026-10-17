import unittest

from susu.money import format_ghs, parse_ghs


class MoneyTests(unittest.TestCase):
    def test_parse_exact(self):
        self.assertEqual(parse_ghs("50"), 5000)
        self.assertEqual(parse_ghs("50.5"), 5050)
        self.assertEqual(parse_ghs("0.10") + parse_ghs("0.20"), parse_ghs("0.30"))

    def test_parse_rejects_bad_input(self):
        for bad in ["abc", "1.234", "nan", "inf", "", 1.5]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                parse_ghs(bad)

    def test_format(self):
        self.assertEqual(format_ghs(15000), "GHS 150.00")
        self.assertEqual(format_ghs(5), "GHS 0.05")
        self.assertEqual(format_ghs(123456789), "GHS 1,234,567.89")
