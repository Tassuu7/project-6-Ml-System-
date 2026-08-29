import unittest
from datamorph.utils.math_utils import mean, median, std_dev, variance, quantile, euclidean_distance, pearson_correlation

class TestMathUtils(unittest.TestCase):
    def test_basic_statistics(self):
        vals = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.assertEqual(mean(vals), 30.0)
        self.assertEqual(median(vals), 30.0)
        self.assertEqual(quantile(vals, 0.5), 30.0)
        self.assertAlmostEqual(variance(vals), 250.0)

    def test_metrics(self):
        v1 = [1.0, 2.0, 3.0]
        v2 = [4.0, 6.0, 8.0]
        self.assertGreater(euclidean_distance(v1, v2), 0)
        self.assertAlmostEqual(pearson_correlation([1, 2, 3, 4], [2, 4, 6, 8]), 1.0)

if __name__ == "__main__":
    unittest.main()
