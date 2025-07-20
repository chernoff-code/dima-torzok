import textwrap
from datetime import timedelta
import re

def format_timestamp(seconds):
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

def smart_split_text(text, max_chars=80):
    """
    Делит текст на части не длиннее max_chars, стараясь делить по . ! ?
    Если таких знаков нет в окне +-10 символов от max_chars, делит по пробелу.
    """
    import re
    parts = []
    while len(text) > max_chars:
        # Ищем ближайший . ! ? в диапазоне [max_chars-10, max_chars+10]
        window = text[max(0, max_chars-10):min(len(text), max_chars+10)]
        m = re.search(r'[.!?]', window)
        if m:
            split_at = max(0, max_chars-10) + m.end()
        else:
            # Если нет подходящего знака, ищем ближайший пробел до max_chars
            space = text.rfind(' ', 0, max_chars)
            split_at = space if space != -1 else max_chars
        parts.append(text[:split_at].strip())
        text = text[split_at:].lstrip()
    if text:
        parts.append(text)
    return parts

def split_long_segments(segments, max_chars=80):
    """
    Делит длинные сегменты на несколько по max_chars, стараясь делить по . ! ?
    Таймкод делится равномерно.
    """
    new_segments = []
    for seg in segments:
        text = seg["text"].strip()
        if len(text) <= max_chars:
            new_segments.append(seg)
            continue
        parts = smart_split_text(text, max_chars)
        n_parts = len(parts)
        starts = [seg["start"] + (seg["end"] - seg["start"]) * i / n_parts for i in range(n_parts)]
        ends = [seg["start"] + (seg["end"] - seg["start"]) * (i+1) / n_parts for i in range(n_parts)]
        for i, part_text in enumerate(parts):
            new_segments.append({
                "start": starts[i],
                "end": ends[i],
                "text": part_text.strip()
            })
    return new_segments

def write_srt(filename, segments, width=80):
    """
    Write subtitle segments to an .srt file.
    Each segment includes a start/end timestamp and wrapped text.
    """
    segments = split_long_segments(segments, max_chars=width)
    segments = remove_leading_dash(segments)
    segments = remove_final_dot_if_single_sentence(segments)
    with open(filename, "w", encoding="utf-8") as srt:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            wrapped = textwrap.fill(seg["text"], width=width)
            srt.write(f"{i}\n{start} --> {end}\n{wrapped}\n\n")

def remove_leading_dash(segments):
    """
    Удаляет ведущие тире/дефисы/длинные тире и пробелы в начале каждой строки субтитра.
    """
    new_segments = []
    for seg in segments:
        text = seg["text"]
        # Удалить только в начале строки: любые тире, дефисы, длинные тире и пробелы
        cleaned = re.sub(r"^[\s\-—–]+", "", text)
        seg = dict(seg)
        seg["text"] = cleaned
        new_segments.append(seg)
    return new_segments

def remove_final_dot_if_single_sentence(segments):
    """
    Если сегмент состоит из одного предложения и заканчивается точкой, точка удаляется.
    """
    import re
    new_segments = []
    for seg in segments:
        text = seg["text"].strip()
        # Проверяем, что только одно предложение (нет других .!? внутри)
        if re.match(r"^[^.?!]+[.]$", text):
            text = text[:-1]
        seg = dict(seg)
        seg["text"] = text
        new_segments.append(seg)
    return new_segments
