import subprocess
import shutil
import librosa
import soundfile as sf
import noisereduce as nr
import sys

def preprocess_audio(input_path, intermediate_path="cleaned.wav", final_path="denoised.wav"):
    """
    Clean audio using FFmpeg filters + denoise with noisereduce.
    Returns path to final cleaned file.
    """

    # 🧰 Проверяем наличие ffmpeg
    if not shutil.which("ffmpeg"):
        print("❌ FFmpeg is not installed or not in PATH.")
        sys.exit(1)

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
        print(f"⚠️ FFmpeg failed: {e}")
        sys.exit(1)

    # 🔕 Шумоподавление
    try:
        y, sr = librosa.load(intermediate_path, sr=None)
        y_denoised = nr.reduce_noise(y=y, sr=sr)
        sf.write(final_path, y_denoised, sr)
    except Exception as e:
        print(f"⚠️ Denoising failed: {e}")
        sys.exit(1)

    return final_path
