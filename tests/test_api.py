import unittest
from datamorph.storage.database import Database
from datamorph.api.auth_router import handle_login
from datamorph.api.dataset_router import handle_upload

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.db = Database(db_path="data/test_db.json")

    def test_auth_login(self):
        code, res = handle_login(self.db, {"username": "admin", "password": "admin123"})
        self.assertEqual(code, 200)
        self.assertIn("token", res)

    def test_upload(self):
        csv_str = "x,y\n1,2\n3,4"
        code, res = handle_upload(self.db, "sample.csv", csv_str)
        self.assertEqual(code, 200)
        self.assertEqual(res["dataset"]["rows"], 2)

if __name__ == "__main__":
    unittest.main()
