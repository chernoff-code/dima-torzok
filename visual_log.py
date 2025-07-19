import logging
import sys
import time
from typing import Optional, Dict

def render_progress_bar(percent: int, width: int = 50, char_full: str = "■", char_empty: str = " ") -> str:
    """
    Generates a string-based progress bar.
    """
    filled = int(width * percent / 100)
    empty = width - filled
    return f"[{char_full * filled}{char_empty * empty}] {percent}%"

def show_progress_block(title: str, percent: int, params: Optional[Dict] = None, delay: float = 0.01):
    """
    Renders styled progress line with optional parameters.
    """
    param_str = ""
    if params:
        param_str = " [" + " | ".join(f"{k}: {v}" for k, v in params.items()) + "]"

    print(f"{title}{param_str}")
    for i in range(0, percent + 1, 5):
        bar = render_progress_bar(i)
        sys.stdout.write(f"\r{bar}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_stage_complete(message: str = "✅ Stage complete."):
    print(message)
