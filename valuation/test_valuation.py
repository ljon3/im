import unittest
from utilities.utils import fullpath
from valuation.Manager import Valuation

class TestMarket(unittest.TestCase):

    def setUp(self):
        pass

    def test_na_in_caps(self):
        value = Valuation(20250331, "caps")
        df_weights = value.valuation_quarterly()
        self.assertEqual(df_weights.isna().sum().sum(), 0.0)

    def test_na_in_msr(self):
        value = Valuation(20250331, "msr")
        df_weights = value.valuation_quarterly()
        self.assertEqual(df_weights.isna().sum().sum(), 0.0)        
