"""
DataMorph Studio - Structured Logging Subsystem
Provides hierarchical, thread-safe structured logging with console and file output.
"""

import sys
import time
import threading
from typing import Dict, Any, Optional

LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


class Logger:
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level_val = LEVELS.get(level.upper(), 20)
        self._lock = threading.Lock()

    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        lvl = LEVELS.get(level, 20)
        if lvl >= self.level_val:
            with self._lock:
                now_str = time.strftime("%Y-%m-%d %H:%M:%S")
                extra_str = f" | {extra}" if extra else ""
                formatted = f"[{now_str}] [{level:7s}] [{self.name}] {message}{extra_str}"
                if lvl >= 40:
                    sys.stderr.write(formatted + "\n")
                    sys.stderr.flush()
                else:
                    sys.stdout.write(formatted + "\n")
                    sys.stdout.flush()

    def debug(self, msg: str, extra: Dict[str, Any] = None):
        self._log("DEBUG", msg, extra)

    def info(self, msg: str, extra: Dict[str, Any] = None):
        self._log("INFO", msg, extra)

    def warning(self, msg: str, extra: Dict[str, Any] = None):
        self._log("WARNING", msg, extra)

    def error(self, msg: str, extra: Dict[str, Any] = None):
        self._log("ERROR", msg, extra)

    def critical(self, msg: str, extra: Dict[str, Any] = None):
        self._log("CRITICAL", msg, extra)


_loggers: Dict[str, Logger] = {}
_logger_lock = threading.Lock()


def get_logger(name: str) -> Logger:
    with _logger_lock:
        if name not in _loggers:
            _loggers[name] = Logger(name)
        return _loggers[name]
