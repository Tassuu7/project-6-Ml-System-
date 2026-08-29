import unittest
from datamorph.connectors.s3_connector import S3StorageConnector
from datamorph.connectors.sql_connector import SQLDatabaseConnector
from datamorph.connectors.snowflake_connector import SnowflakeWarehouseConnector
from datamorph.connectors.kafka_connector import KafkaStreamConnector
from datamorph.connectors.rest_connector import RestAPIConnector

class TestConnectors(unittest.TestCase):
    def test_s3_connector(self):
        s3 = S3StorageConnector(bucket_name="datamorph-ml-lake")
        self.assertTrue(s3.connect())
        df = s3.fetch_data("s3://bucket/test.csv")
        self.assertEqual(len(df), 5)
        objs = s3.list_objects()
        self.assertEqual(len(objs), 3)

    def test_sql_connector(self):
        sql = SQLDatabaseConnector(connection_url="postgresql://user:pass@localhost/db")
        self.assertTrue(sql.connect())
        df = sql.fetch_data("SELECT * FROM metrics")
        self.assertEqual(len(df), 4)

    def test_snowflake_connector(self):
        sf = SnowflakeWarehouseConnector(account="xy12345", warehouse="COMPUTE_WH", database="ML_DB", schema="PUBLIC")
        self.assertTrue(sf.connect())
        df = sf.fetch_data("SELECT * FROM features")
        self.assertEqual(len(df), 3)

    def test_kafka_connector(self):
        kafka = KafkaStreamConnector(bootstrap_servers=["localhost:9092"], topic="telemetry_stream")
        self.assertTrue(kafka.connect())
        df = kafka.fetch_data("telemetry_stream")
        self.assertEqual(len(df), 5)

    def test_rest_connector(self):
        rest = RestAPIConnector(endpoint_url="https://api.datamorph.ai/v1/metrics")
        self.assertTrue(rest.connect())
        df = rest.fetch_data("/v1/metrics")
        self.assertEqual(len(df), 3)

if __name__ == "__main__":
    unittest.main()
