import unittest
from datamorph.core.dataframe import DataFrame, Series
from datamorph.core.types import DataType

class TestCoreDataFrame(unittest.TestCase):
    def setUp(self):
        self.df = DataFrame({
            "age": [25, 30, 35, None, 45],
            "salary": [50000.0, 60000.0, 75000.0, 80000.0, 110000.0],
            "dept": ["HR", "Engineering", "Marketing", "HR", "Engineering"]
        })

    def test_shape_and_columns(self):
        self.assertEqual(self.df.shape, (5, 3))
        self.assertEqual(self.df.columns, ["age", "salary", "dept"])

    def test_series_statistics(self):
        s_salary = self.df["salary"]
        self.assertEqual(s_salary.mean(), 75000.0)
        self.assertEqual(s_salary.median(), 75000.0)
        self.assertEqual(s_salary.min(), 50000.0)
        self.assertEqual(s_salary.max(), 110000.0)

    def test_missing_values(self):
        s_age = self.df["age"]
        self.assertEqual(s_age.missing_count(), 1)
        self.assertEqual(s_age.missing_percentage(), 20.0)
        filled = s_age.fillna(30)
        self.assertEqual(filled.missing_count(), 0)

    def test_add_drop_column(self):
        df_new = self.df.drop_column("dept")
        self.assertEqual(df_new.columns, ["age", "salary"])
        df_new.add_column("bonus", [1000, 2000, 3000, 4000, 5000])
        self.assertIn("bonus", df_new.columns)

    def test_slice_head(self):
        head_df = self.df.head(2)
        self.assertEqual(len(head_df), 2)
        self.assertEqual(head_df["dept"].to_list(), ["HR", "Engineering"])

if __name__ == "__main__":
    unittest.main()
