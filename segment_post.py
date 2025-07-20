
from typing import List, Dict, Any

def merge_short_segments(segments: List[Dict[str, Any]], min_word_count: int = 3, max_pause: float = 1.0) -> List[Dict[str, Any]]:
    """
    Объединяет слишком короткие сегменты (по количеству слов) с предыдущим,
    если между ними небольшая пауза.
    """
    if not segments:
        return []
    merged = []
    for seg in segments:
        words = seg["text"].strip().split()
        if (len(words) < min_word_count and merged and
            seg["start"] - merged[-1]["end"] < max_pause):
            merged[-1]["text"] = merged[-1]["text"].rstrip() + " " + seg["text"].lstrip()
            merged[-1]["end"] = seg["end"]
        else:
            merged.append(dict(seg))
    return merged
