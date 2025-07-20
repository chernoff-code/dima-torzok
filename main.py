
import sys
import os
from datetime import datetime

# --- Перенаправление stderr Vosk в файл до любых импортов vosk/diarization_utils ---

# --- Перенаправление stderr Vosk в файл, но только после определения session_dir ---


from audio_utils import preprocess_audio
from segment_filter import process_segments, load_hallucination_markers
from segment_stack import stack_repeated_segments
from segment_post import merge_short_segments
from subtitle_io import write_srt, remove_leading_dash, remove_final_dot_if_single_sentence
from translate_utils import translate_segments
from visual_log import show_progress_block, show_stage_complete
from diarization_utils import diarize_audio_vosk, assign_speakers_to_segments
import urllib.request
import tarfile

import whisper
import argparse
import time

def get_session_dir(audio_path, dt=None):
    base = os.path.splitext(os.path.basename(audio_path))[0]
    if dt is None:
        dt = datetime.now()
    session = f"sessions/{base}_" + dt.strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(session, exist_ok=True)
    return session

def download_and_extract(url, dest_dir):
    import os
    import shutil
    import zipfile
    filename = url.split('/')[-1]
    archive_path = os.path.join(dest_dir, filename)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    if not os.path.exists(archive_path):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, archive_path)
    print(f"Extracting {filename}...")
    if filename.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
    else:
        with tarfile.open(archive_path, 'r:*') as tar:
            tar.extractall(dest_dir)
    # Remove archive after extraction
    os.remove(archive_path)

def main():
    import sys
    parser = argparse.ArgumentParser(description="DimaTorzok v1.0.0 - Russian Audio Transcription and Translation")
    parser.add_argument("file_path", help="Path to input media file")
    parser.add_argument("--model", default="large", help="Whisper model (base, small, medium, turbo, large)")
    parser.add_argument("--hallucination-file", help="Path to hallucination phrases file")
    args = parser.parse_args()

    # фиксируем время запуска один раз
    session_dir = get_session_dir(args.file_path)
    # Перенаправляем stderr Vosk сразу в нужный vosk.log
    vosk_log_path = os.path.join(session_dir, "vosk.log")
    vosk_log_file = open(vosk_log_path, "w", encoding="utf-8")
    old_stderr = sys.stderr
    sys.stderr = vosk_log_file

    # Проверяем и скачиваем Vosk модели при необходимости
    vosk_model_url = "https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip"
    vosk_spk_url = "https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip"
    vosk_model_dir = "vosk-model-ru-0.22"
    vosk_spk_dir = "vosk-model-spk-0.4"
    if not os.path.exists(vosk_model_dir):
        download_and_extract(vosk_model_url, ".")
    if not os.path.exists(vosk_spk_dir):
        download_and_extract(vosk_spk_url, ".")

    # 🔊 Этап 1: Предобработка аудио
    show_progress_block("🧼 Audio preprocessing...", 100, {
        "speed": "simulated 120x",
        "bitrate": "1411kbit/s"
    })
    cleaned_audio = preprocess_audio(args.file_path, session_dir=session_dir)
    show_stage_complete("✅ Preprocessing complete.")

    # 🔄 Этап 2: Загрузка модели
    print(f"🔄 Loading Whisper model: {args.model}")
    model = whisper.load_model(args.model)

    # 🗣️ 🤖 Этап 3: Транскрибирование
    print("🗣️ 🤖 Transcribing audio...")
    start_time = time.time()
    result = model.transcribe(
        cleaned_audio,
        language="Russian",
        condition_on_previous_text=False,
        verbose=False,
        temperature=0
    )
    elapsed = time.time() - start_time
    segments = result["segments"]
    rate = round(len(segments) / elapsed, 2)
    show_progress_block("🗣️ 🤖 Transcribing audio...", 100, {
        "segments": len(segments),
        "rate": f"{rate} seg/s"
    })

    # Диаризация Vosk
    show_progress_block("🔎 Running speaker diarization (Vosk)...", 30, {"stage": "diarization"})
    try:
        speaker_segments = diarize_audio_vosk(cleaned_audio, vosk_model_dir, vosk_spk_dir)
        show_stage_complete("✅ Speaker diarization complete.")
    except Exception as e:
        print(f"[WARN] Speaker diarization failed: {e}")
        speaker_segments = None
    finally:
        sys.stderr = old_stderr
        vosk_log_file.close()

    # Присваиваем спикеров сегментам, если удалось получить diarization
    if speaker_segments:
        segments = assign_speakers_to_segments(segments, speaker_segments)

    show_stage_complete("✅ Transcription finished.")

    # 📜 Этап 4: Фильтрация и стакание
    hallucinations = load_hallucination_markers(args.hallucination_file)
    segments = process_segments(segments, session_dir, hallucination_markers=hallucinations)
    segments = stack_repeated_segments(segments)
    segments = merge_short_segments(segments, min_word_count=3, max_pause=1.0)

    # Удаляем тире в начале и точку в конце только перед записью и переводом
    segments = remove_leading_dash(segments)
    segments = remove_final_dot_if_single_sentence(segments)

    print("📜 Writing Russian subtitles...")
    write_srt(os.path.join(session_dir, "output_ru.srt"), segments)
    print(f"📁 Saved: {os.path.join(session_dir, 'output_ru.srt')}")
    print(f"📁 Repetition log: {os.path.join(session_dir, 'repetitions.log')}")

    # 🌍 Этап 5: Перевод
    print("🌍 Translating subtitles... [segments:", len(segments), "]")
    translated = translate_segments(segments)
    translated = remove_leading_dash(translated)
    translated = remove_final_dot_if_single_sentence(translated)
    show_stage_complete("✅ Translation complete.")
    write_srt(os.path.join(session_dir, "output_en_translated.srt"), translated)
    print(f"📁 Saved: {os.path.join(session_dir, 'output_en_translated.srt')}\n")

if __name__ == "__main__":
    main()
