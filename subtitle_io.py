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

def split_long_segments(segments: List[Dict[str, Any]], max_chars: int = 80) -> List[Dict[str, Any]]:
    """
    Делит длинные сегменты на несколько по max_chars, равномерно делит таймкод.
    """
    new_segments = []
    for seg in segments:
        text = seg["text"].strip()
        if len(text) <= max_chars:
            new_segments.append(seg)
            continue
        # Сколько частей?
        n_parts = (len(text) + max_chars - 1) // max_chars
        part_len = len(text) // n_parts
        starts = [seg["start"] + (seg["end"] - seg["start"]) * i / n_parts for i in range(n_parts)]
        ends = [seg["start"] + (seg["end"] - seg["start"]) * (i+1) / n_parts for i in range(n_parts)]
        for i in range(n_parts):
            part_text = text[i*part_len:(i+1)*part_len] if i < n_parts-1 else text[i*part_len:]
            new_segments.append({
                "start": starts[i],
                "end": ends[i],
                "text": part_text.strip()
            })
    return new_segments
