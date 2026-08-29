import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.imputation.simple import SimpleImputer
from datamorph.transformers.imputation.knn import KNNImputer
from datamorph.transformers.imputation.indicator import MissingIndicator

class TestImputation(unittest.TestCase):
    def setUp(self):
        self.df = DataFrame({
            "val": [10.0, None, 30.0, 40.0, None],
            "cat": ["A", "B", None, "A", "A"]
        })

    def test_mean_imputation(self):
        imp = SimpleImputer(strategy="mean", columns=["val"])
        res = imp.fit_transform(self.df)
        self.assertEqual(res["val"].missing_count(), 0)
        self.assertEqual(res["val"][1], 26.666666666666668)

    def test_mode_imputation(self):
        imp = SimpleImputer(strategy="mode", columns=["cat"])
        res = imp.fit_transform(self.df)
        self.assertEqual(res["cat"].missing_count(), 0)
        self.assertEqual(res["cat"][2], "A")

    def test_missing_indicator(self):
        ind = MissingIndicator(columns=["val"])
        res = ind.fit_transform(self.df)
        self.assertIn("missing_val", res.columns)
        self.assertEqual(res["missing_val"].to_list(), [0, 1, 0, 0, 1])

if __name__ == "__main__":
    unittest.main()
