import logging
from typing import List, Dict, Any
from utils import format_timestamp
import textwrap

def write_srt(filename: str, segments: List[Dict[str, Any]]):
    """
    Write subtitle segments to an .srt file.
    Each segment includes a start/end timestamp and wrapped text.
    """
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
