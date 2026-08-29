import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.scaling.standard import StandardScaler
from datamorph.transformers.scaling.minmax import MinMaxScaler
from datamorph.transformers.scaling.robust import RobustScaler

class TestScaling(unittest.TestCase):
    def setUp(self):
        self.df = DataFrame({"feat": [10.0, 20.0, 30.0, 40.0, 50.0]})

    def test_standard_scaler(self):
        scaler = StandardScaler(columns=["feat"])
        res = scaler.fit_transform(self.df)
        self.assertAlmostEqual(res["feat"].mean(), 0.0, places=4)
        self.assertAlmostEqual(res["feat"].std(), 1.0, places=4)

    def test_minmax_scaler(self):
        scaler = MinMaxScaler(columns=["feat"])
        res = scaler.fit_transform(self.df)
        self.assertEqual(res["feat"].min(), 0.0)
        self.assertEqual(res["feat"].max(), 1.0)

    def test_robust_scaler(self):
        scaler = RobustScaler(columns=["feat"])
        res = scaler.fit_transform(self.df)
        self.assertEqual(res["feat"][2], 0.0)  # median centered

if __name__ == "__main__":
    unittest.main()
