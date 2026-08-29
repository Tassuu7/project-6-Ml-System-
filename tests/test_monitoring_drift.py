import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.monitoring.drift_detector import DriftDetector

class TestDriftDetector(unittest.TestCase):
    def test_psi_and_ks(self):
        det = DriftDetector()
        base = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        drifted = [20.0, 22.0, 24.0, 25.0, 28.0, 30.0, 32.0, 35.0, 38.0, 40.0]
        psi = det.calculate_psi(base, drifted)
        ks = det.calculate_ks_statistic(base, drifted)
        self.assertGreater(psi, 0.0)
        self.assertEqual(ks, 1.0)

if __name__ == "__main__":
    unittest.main()
