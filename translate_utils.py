import logging
import requests
import threading
import json
import sys
import itertools
from typing import List, Dict, Any

def translate_text_local(text: str) -> str:
    """
    Translate a given text from Russian to English using local LibreTranslate API.
    Fallbacks to first alternative if direct translation is missing.
    """
    url = "http://translate.localhost/translate"
    data = {
        "q": text,
        "source": "ru",
        "target": "en",
        "format": "text",
        "alternatives": 1
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        parsed = response.json()
        if "translatedText" in parsed:
            return parsed["translatedText"]
        elif "alternatives" in parsed and parsed["alternatives"]:
            return parsed["alternatives"][0]
        else:
            logging.warning(f"Unexpected response keys: {list(parsed.keys())}")
            return ""
    except Exception as e:
        logging.error(f"LibreTranslate error: {e}")
        if 'response' in locals():
            logging.error(f"Raw response: {response.text}")
        return ""

def spin_earth(stop_event):
    """
    Simple spinner to indicate translation progress.
    """
    globe = itertools.cycle(["🌍", "🌎", "🌏"])
    while not stop_event.is_set():
        sys.stdout.write(f"\r{next(globe)} Translating subtitles...")
        sys.stdout.flush()
        stop_event.wait(0.3)
    print("\r✅ Translation complete.         ")

def translate_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Translate list of segments and show a spinner while working.
    Returns list of translated subtitle blocks.
    """
    translated = []
    stop_event = threading.Event()
    spinner = threading.Thread(target=spin_earth, args=(stop_event,))
    spinner.start()

    for seg in segments:
        translated_text = translate_text_local(seg["text"])
        translated.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": translated_text
        })

    stop_event.set()
    spinner.join()
    return translated
