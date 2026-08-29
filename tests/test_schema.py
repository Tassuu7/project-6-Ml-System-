import unittest
from datamorph.core.schema import Schema, Field
from datamorph.core.types import DataType

class TestSchema(unittest.TestCase):
    def test_schema_field_validation(self):
        f = Field(name="score", dtype=DataType.NUMERIC_FLOAT, min_value=0.0, max_value=100.0, nullable=False)
        valid, err = f.validate_value(85.5)
        self.assertTrue(valid)
        
        valid_invalid, err_invalid = f.validate_value(150.0)
        self.assertFalse(valid_invalid)
        
        valid_null, err_null = f.validate_value(None)
        self.assertFalse(valid_null)

    def test_schema_container(self):
        s = Schema([
            Field(name="id", dtype=DataType.NUMERIC_INT, is_primary_key=True),
            Field(name="label", dtype=DataType.CATEGORICAL_NOMINAL, is_target=True)
        ])
        self.assertEqual(s.target_feature, "label")
        self.assertEqual(len(s.fields), 2)

if __name__ == "__main__":
    unittest.main()
