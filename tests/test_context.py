import unittest
from datamorph.core.context import ExecutionContext

class TestContext(unittest.TestCase):
    def test_context_lifecycle(self):
        ctx = ExecutionContext(user_id="test_user")
        t = ctx.start_step("step1", "ImputationStep")
        self.assertEqual(t.status, "running")
        ctx.complete_step("step1", rows_in=100, rows_out=100, cols_in=5, cols_out=5)
        summary = ctx.get_execution_summary()
        self.assertEqual(summary["step_count"], 1)
        self.assertEqual(summary["steps"][0]["status"], "completed")

if __name__ == "__main__":
    unittest.main()
