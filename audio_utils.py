import logging
import subprocess
import shutil
import librosa
import soundfile as sf
import noisereduce as nr
import os
from datetime import datetime
from typing import Optional

def preprocess_audio(input_path: str, session_dir: str, intermediate_path: str = None, final_path: str = None) -> str:
    if not intermediate_path:
        intermediate_path = os.path.join(session_dir, "cleaned.wav")
    if not final_path:
        final_path = os.path.join(session_dir, "denoised.wav")

    """
    Clean audio using FFmpeg filters + denoise with noisereduce.
    Returns path to final cleaned file.
    """

    # 🧰 Проверяем наличие ffmpeg
    if not shutil.which("ffmpeg"):
        logging.error("FFmpeg is not installed or not in PATH.")
        raise RuntimeError("FFmpeg is not installed or not in PATH.")

    # 🎧 Применяем аудиофильтры: обрезаем низкие/высокие частоты, нормализуем, подавляем шум
    filters = "highpass=f=200, lowpass=f=3000, afftdn, dynaudnorm"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-af", filters, intermediate_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except Exception as e:
        logging.error(f"FFmpeg failed: {e}")
        raise

    # 🔕 Шумоподавление
    try:
        y, sr = librosa.load(intermediate_path, sr=None)
        y_denoised = nr.reduce_noise(y=y, sr=sr)
        sf.write(final_path, y_denoised, sr)
    except Exception as e:
        logging.error(f"Denoising failed: {e}")
        raise

    return final_path
