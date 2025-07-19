import textwrap
from datetime import timedelta

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

def write_srt(filename, segments):
    """
    Write subtitle segments to an .srt file.
    Each segment includes a start/end timestamp and wrapped text.
    """
    with open(filename, "w", encoding="utf-8") as srt:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            wrapped = textwrap.fill(seg["text"], width=80)
            srt.write(f"{i}\n{start} --> {end}\n{wrapped}\n\n")
