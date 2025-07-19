import pytest
from audio_utils import preprocess_audio

def test_preprocess_audio_missing_ffmpeg(monkeypatch):
    import shutil
    monkeypatch.setattr(shutil, "which", lambda x: None)
    try:
        preprocess_audio("fake.wav")
    except RuntimeError as e:
        assert "FFmpeg is not installed" in str(e)
    else:
        assert False, "Expected RuntimeError for missing ffmpeg"
