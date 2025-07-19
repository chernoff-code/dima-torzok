import logging
import re
import os
from typing import Optional, List, Dict, Any
from utils import format_timestamp
from datetime import timedelta, datetime

# 📆 Форматирование таймкодов
def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((seconds - total_seconds) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# 🧠 Повторяющиеся фразы
def is_repetitive(text: str, threshold: float = 0.6, max_repeat: int = 10) -> bool:
    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return False
    unique = set(words)
    ratio = len(unique) / len(words)
    return ratio < threshold or any(words.count(w) > max_repeat for w in unique)

# ❌ Нестабильные сегменты
def is_unreliable(text: str, segment: Dict[str, Any]) -> bool:
    return (
        not text or
        segment.get("no_speech_prob", 0) > 0.5 or
        len(text.strip()) < 4 or
        is_repetitive(text)
    )

# 🚫 Загрузка стоп-фраз
def load_hallucination_markers(path: Optional[str]) -> List[str]:
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# 📌 Проверка текста на галлюцинации
def is_hallucination(text: str, markers: List[str]) -> bool:
    return any(marker.lower() in text.lower() for marker in markers)

def remove_hallucinations(text: str, markers: List[str]) -> str:
    for marker in markers:
        text = re.sub(re.escape(marker), "", text, flags=re.IGNORECASE)
    return text.strip()

def get_session_dir() -> str:
    session = datetime.now().strftime("sessions/%Y-%m-%d_%H-%M-%S")
    os.makedirs(session, exist_ok=True)
    return session

# 🧹 Обработка сегментов + логирование болтовни
def process_segments(segments: List[Dict[str, Any]], rep_log_path: str = None, hallucination_markers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    if rep_log_path is None:
        rep_log_path = os.path.join(get_session_dir(), "repetitions.log")
    final = []
    with open(rep_log_path, "w", encoding="utf-8") as rep_log:
        for seg in segments:
            text = seg["text"].strip()
            if is_unreliable(text, seg):
                if is_repetitive(text):
                    rep_log.write(f"[{format_timestamp(seg['start'])}] {text}\n\n")
                continue

            if hallucination_markers and is_hallucination(text, hallucination_markers):
                cleaned = remove_hallucinations(text, hallucination_markers)
                if not cleaned:
                    continue
                text = cleaned

            final.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": text
            })
    return final
