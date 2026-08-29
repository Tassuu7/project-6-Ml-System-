import unittest
from datamorph.core.dataframe import DataFrame
from datamorph.pipeline.dag import PipelineDAG
from datamorph.pipeline.step import PipelineStep
from datamorph.pipeline.runner import PipelineRunner
from datamorph.transformers.imputation.simple import SimpleImputer
from datamorph.transformers.scaling.standard import StandardScaler

class TestDAGPipeline(unittest.TestCase):
    def test_dag_execution_flow(self):
        df = DataFrame({"val": [10.0, None, 30.0, 40.0, 50.0]})
        dag = PipelineDAG(name="TestDAG")
        s1 = PipelineStep(name="impute", transformer=SimpleImputer(strategy="mean", columns=["val"]))
        s2 = PipelineStep(name="scale", transformer=StandardScaler(columns=["val"]), depends_on=[s1.step_id])
        dag.add_step(s1)
        dag.add_step(s2)

        runner = PipelineRunner()
        res = runner.run(dag, df)
        self.assertEqual(res["val"].missing_count(), 0)
        self.assertAlmostEqual(res["val"].mean(), 0.0, places=3)

if __name__ == "__main__":
    unittest.main()
