import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.discretization.equal_width import EqualWidthDiscretizer

class TestDiscretization(unittest.TestCase):
    def test_equal_width(self):
        df = DataFrame({"score": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]})
        dis = EqualWidthDiscretizer(n_bins=5, columns=["score"])
        res = dis.fit_transform(df)
        self.assertIn("score_binned", res.columns)
        self.assertEqual(len(res["score_binned"]), 10)

if __name__ == "__main__":
    unittest.main()
