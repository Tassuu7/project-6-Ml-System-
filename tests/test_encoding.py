import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.encoding.onehot import OneHotEncoder
from datamorph.transformers.encoding.ordinal import OrdinalEncoder
from datamorph.transformers.encoding.frequency import FrequencyEncoder

class TestEncoding(unittest.TestCase):
    def setUp(self):
        self.df = DataFrame({"color": ["red", "blue", "red", "green"]})

    def test_onehot_encoder(self):
        enc = OneHotEncoder(columns=["color"])
        res = enc.fit_transform(self.df)
        self.assertIn("color_red", res.columns)
        self.assertIn("color_blue", res.columns)

    def test_ordinal_encoder(self):
        enc = OrdinalEncoder(columns=["color"])
        res = enc.fit_transform(self.df)
        self.assertEqual(len(set(res["color"].to_list())), 3)

    def test_frequency_encoder(self):
        enc = FrequencyEncoder(columns=["color"])
        res = enc.fit_transform(self.df)
        self.assertEqual(res["color"][0], 0.5)

if __name__ == "__main__":
    unittest.main()
