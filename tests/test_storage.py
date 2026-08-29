import unittest
import os
from datamorph.core.dataframe import DataFrame
from datamorph.storage.writer import DatasetWriter
from datamorph.storage.reader import DatasetReader

class TestStorage(unittest.TestCase):
    def test_csv_read_write(self):
        df = DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        tmp_path = "data/test_out.csv"
        DatasetWriter.write_csv(df, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))
        
        loaded = DatasetReader.read_csv(tmp_path)
        self.assertEqual(loaded.shape, (3, 2))
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()
