"""
DataMorph Studio - Alert & Notification Management
Dispatches data drift alerts, schema violation notifications, and pipeline failure events.
"""

import time
from typing import Dict, List, Any


class AlertManager:
    def __init__(self):
        self._alerts: List[Dict[str, Any]] = []

    def trigger_alert(self, level: str, title: str, message: str, details: Dict[str, Any] = None):
        alert = {
            "id": f"alert_{int(time.time() * 1000)}",
            "level": level.upper(),  # INFO, WARNING, CRITICAL
            "title": title,
            "message": message,
            "timestamp": time.time(),
            "details": details or {}
        }
        self._alerts.append(alert)

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return list(reversed(self._alerts))

    def clear_alerts(self):
        self._alerts.clear()
