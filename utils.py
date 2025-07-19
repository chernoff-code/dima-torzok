"""
Common utility functions for timestamp formatting and other helpers.
"""
from datetime import timedelta

def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format: HH:MM:SS,mmm
    """
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((seconds - total_seconds) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
