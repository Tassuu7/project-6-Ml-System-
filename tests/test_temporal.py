import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.temporal.cyclical import CyclicalDateTimeEncoder
from datamorph.transformers.temporal.lag_lead import LagLeadFeatureGenerator

class TestTemporal(unittest.TestCase):
    def test_cyclical_encoder(self):
        df = DataFrame({"hour": [0, 6, 12, 18, 23]})
        enc = CyclicalDateTimeEncoder(columns=["hour"])
        res = enc.fit_transform(df)
        self.assertIn("hour_sin", res.columns)
        self.assertIn("hour_cos", res.columns)

    def test_lag_generator(self):
        df = DataFrame({"price": [100, 102, 105, 108, 110]})
        gen = LagLeadFeatureGenerator(lags=[1], columns=["price"])
        res = gen.fit_transform(df)
        self.assertIn("price_lag_1", res.columns)
        self.assertIsNone(res["price_lag_1"][0])
        self.assertEqual(res["price_lag_1"][1], 100)

if __name__ == "__main__":
    unittest.main()
