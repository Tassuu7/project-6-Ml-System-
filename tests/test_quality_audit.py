import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.monitoring.quality_audit import DataQualityAuditor

class TestQualityAudit(unittest.TestCase):
    def test_audit_score(self):
        df = DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [None, None, None, None, None]
        })
        auditor = DataQualityAuditor()
        rep = auditor.audit(df)
        self.assertIn("quality_score", rep)
        self.assertLess(rep["quality_score"], 100.0)

if __name__ == "__main__":
    unittest.main()
