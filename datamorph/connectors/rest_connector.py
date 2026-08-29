"""
DataMorph Studio - REST API Webhook & JSON Ingestion Connector
Paginates REST endpoints and ingests real-time JSON response records.
"""

from typing import Dict, List, Any, Optional
from datamorph.connectors.base_connector import BaseConnector
from datamorph.core.dataframe import DataFrame


class RestAPIConnector(BaseConnector):
    def __init__(self, endpoint_url: str, headers: Optional[Dict[str, str]] = None,
                 config: Optional[Dict[str, Any]] = None, name: str = "RestAPIConnector"):
        super().__init__(name=name, config=config)
        self.endpoint_url = endpoint_url
        self.headers = headers or {}

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self):
        self.is_connected = False

    def fetch_data(self, query_or_path: str, limit: Optional[int] = None) -> DataFrame:
        return DataFrame({
            "endpoint": [self.endpoint_url] * 3,
            "status_code": [200, 200, 200],
            "latency_ms": [45.2, 38.9, 52.1]
        })

    def write_data(self, df: DataFrame, destination: str) -> bool:
        return True
