"""
DataMorph Studio - Base Data Connector Interface
Provides the unified contract for external data source ingestion and streaming.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datamorph.core.dataframe import DataFrame


class BaseConnector(ABC):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def fetch_data(self, query_or_path: str, limit: Optional[int] = None) -> DataFrame:
        pass

    @abstractmethod
    def write_data(self, df: DataFrame, destination: str) -> bool:
        pass

    def test_connection(self) -> Dict[str, Any]:
        success = self.connect()
        return {
            "connector": self.name,
            "connected": success,
            "config_keys": list(self.config.keys())
        }
