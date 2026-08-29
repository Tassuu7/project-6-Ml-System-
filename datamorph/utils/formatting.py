"""
DataMorph Studio - Formatting & Display Utilities
Formats bytes, durations, numbers, tables, and execution metrics.
"""

from typing import Union, List, Dict, Any


def format_bytes(size_bytes: Union[int, float]) -> str:
    """Formats bytes into human-readable units (B, KB, MB, GB, TB)."""
    if size_bytes is None or size_bytes < 0:
        return "0 B"
    size = float(size_bytes)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    """Formats seconds into human-readable duration."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} µs"
    elif seconds < 1.0:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60.0:
        return f"{seconds:.2f} s"
    elif seconds < 3600.0:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def format_number(val: Union[int, float], decimals: int = 2) -> str:
    """Formats float or integer with thousand separators."""
    if val is None:
        return "N/A"
    if isinstance(val, int):
        return f"{val:,}"
    return f"{val:,.{decimals}f}"
