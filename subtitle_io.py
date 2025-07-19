import logging
from typing import List, Dict, Any
from utils import format_timestamp
import textwrap
import os
from datetime import datetime

def get_session_dir() -> str:
    session = datetime.now().strftime("sessions/%Y-%m-%d_%H-%M-%S")
    os.makedirs(session, exist_ok=True)
    return session

def write_srt(filename: str, segments: List[Dict[str, Any]]):
    """
    Write subtitle segments to an .srt file.
    Each segment includes a start/end timestamp and wrapped text.
    """
    session_dir = get_session_dir()
    filename = os.path.join(session_dir, os.path.basename(filename))
    
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
