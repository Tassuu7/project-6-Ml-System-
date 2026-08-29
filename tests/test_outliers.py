import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.outliers.zscore import ZScoreOutlierDetector
from datamorph.transformers.outliers.iqr import IQROutlierRemover
from datamorph.transformers.outliers.winsorizer import Winsorizer

class TestOutliers(unittest.TestCase):
    def setUp(self):
        self.df = DataFrame({"val": [10.0, 12.0, 11.0, 10.0, 10.5, 11.2, 9.8, 10.1, 1000.0]})

    def test_zscore_clipper(self):
        det = ZScoreOutlierDetector(threshold=2.0, action="clip", columns=["val"])
        res = det.fit_transform(self.df)
        self.assertLess(res["val"][8], 1000.0)

    def test_winsorizer(self):
        win = Winsorizer(lower_quantile=0.05, upper_quantile=0.80, columns=["val"])
        res = win.fit_transform(self.df)
        self.assertLess(res["val"][4], 1000.0)

if __name__ == "__main__":
    unittest.main()
