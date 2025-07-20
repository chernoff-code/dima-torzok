"""
diarization_utils.py
Speaker diarization utilities using Vosk (no registration or tokens required).
"""

from typing import List, Dict, Any
import wave
import os

try:
    from vosk import Model, KaldiRecognizer, SpkModel
except ImportError:
    Model = None
    KaldiRecognizer = None
    SpkModel = None


def diarize_audio_vosk(audio_path: str, model_path: str = "vosk-model-small-ru-0.22", spk_model_path: str = "vosk-model-spk-0.4") -> List[Dict[str, Any]]:
    """
    Run speaker diarization using Vosk and return a list of speaker segments.
    Each segment: {"start": float, "end": float, "speaker": str}
    """
    if Model is None or KaldiRecognizer is None or SpkModel is None:
        raise ImportError("vosk is not installed. Please install it with 'pip install vosk'.")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Vosk model not found at {model_path}. Download from https://alphacephei.com/vosk/models")
    if not os.path.exists(spk_model_path):
        raise FileNotFoundError(f"Vosk speaker model not found at {spk_model_path}. Download from https://alphacephei.com/vosk/models")

    wf = wave.open(audio_path, "rb")
    model = Model(model_path)
    spk_model = SpkModel(spk_model_path)
    rec = KaldiRecognizer(model, wf.getframerate(), spk_model)
    rec.SetWords(True)
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = rec.Result()
            results.append(res)
    results.append(rec.FinalResult())
    wf.close()

    import json
    speaker_segments = []
    for res in results:
        jres = json.loads(res)
        if 'spk' in jres and 'result' in jres:
            for word in jres['result']:
                speaker_segments.append({
                    "start": word['start'],
                    "end": word['end'],
                    "speaker": f"spk{jres['spk']}"
                })
    return speaker_segments


def assign_speakers_to_segments(segments: List[Dict[str, Any]], speaker_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assign speaker labels to Whisper segments based on overlap with diarization segments.
    Adds a 'speaker' key to each segment.
    """
    for seg in segments:
        seg_start = seg.get("start", 0)
        seg_end = seg.get("end", 0)
        max_overlap = 0
        assigned_speaker = None
        for spk in speaker_segments:
            overlap = min(seg_end, spk["end"]) - max(seg_start, spk["start"])
            if overlap > max_overlap and overlap > 0:
                max_overlap = overlap
                assigned_speaker = spk["speaker"]
        seg["speaker"] = assigned_speaker or "Unknown"
    return segments
