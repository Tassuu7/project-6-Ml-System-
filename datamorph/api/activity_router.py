"""
DataMorph Studio - Activity & Audit Trail API Router
Records and retrieves real system events, notifications, and user actions.
"""

import time
from typing import Dict, List, Any, Optional

def log_system_activity(db, action_type: str, title: str, details: str, metadata: Optional[Dict[str, Any]] = None, level: str = "info"):
    """Appends an event record to the database audit trail and notification queue."""
    event = {
        "id": f"act_{int(time.time() * 1000)}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "action_type": action_type,
        "title": title,
        "details": details,
        "metadata": metadata or {},
        "level": level,  # info, warning, success, error
        "read": False
    }
    db.append("audit_logs", event)
    return event

def handle_get_activities(db, limit: int = 50) -> tuple:
    """Returns the most recent activity items."""
    logs = db.get_all("audit_logs")
    if isinstance(logs, dict):
        logs = list(logs.values())
    elif not isinstance(logs, list):
        logs = []
    
    # Sort newest first
    sorted_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
    return 200, {
        "status": "success",
        "activities": sorted_logs[:limit],
        "total_count": len(sorted_logs)
    }

def handle_get_notifications(db) -> tuple:
    """Returns active unread and recent notifications."""
    logs = db.get_all("audit_logs")
    if isinstance(logs, dict):
        logs = list(logs.values())
    elif not isinstance(logs, list):
        logs = []
    
    notifications = [l for l in logs if l.get("level") in ("warning", "error", "success")]
    sorted_notifs = sorted(notifications, key=lambda x: x.get("timestamp", ""), reverse=True)
    unread_count = sum(1 for n in sorted_notifs if not n.get("read", False))
    
    return 200, {
        "status": "success",
        "unread_count": unread_count,
        "notifications": sorted_notifs[:20]
    }
