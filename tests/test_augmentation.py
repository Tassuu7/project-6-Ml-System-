import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.transformers.augmentation.noise_injection import GaussianNoiseInjector

class TestAugmentation(unittest.TestCase):
    def test_noise_injector(self):
        df = DataFrame({"feat": [10.0, 20.0, 30.0, 40.0]})
        inj = GaussianNoiseInjector(noise_std=0.01, columns=["feat"])
        res = inj.fit_transform(df)
        self.assertNotEqual(res["feat"].to_list(), df["feat"].to_list())

if __name__ == "__main__":
    unittest.main()
