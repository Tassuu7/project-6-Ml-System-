import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.selection.variance import VarianceThresholdSelector

class TestSelection(unittest.TestCase):
    def test_variance_threshold(self):
        df = DataFrame({
            "constant": [1, 1, 1, 1, 1],
            "variable": [10, 20, 30, 40, 50]
        })
        sel = VarianceThresholdSelector(threshold=0.0, columns=["constant", "variable"])
        res = sel.fit_transform(df)
        self.assertNotIn("constant", res.columns)
        self.assertIn("variable", res.columns)

if __name__ == "__main__":
    unittest.main()
