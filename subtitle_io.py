import logging
from typing import List, Dict, Any
from utils import format_timestamp
import textwrap
import os
from datetime import datetime

def write_srt(filename: str, segments: List[Dict[str, Any]]):
    try:
        with open(filename, "w", encoding="utf-8") as srt:
            for i, seg in enumerate(segments, 1):
                start = format_timestamp(seg["start"])
                end = format_timestamp(seg["end"])
                wrapped = textwrap.fill(seg["text"], width=80)
                srt.write(f"{i}\n{start} --> {end}\n{wrapped}\n\n")
    except Exception as e:
        logging.error(f"Failed to write SRT: {e}")
        raise
