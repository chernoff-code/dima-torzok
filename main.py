import logging
from audio_utils import preprocess_audio
from segment_filter import process_segments, load_hallucination_markers
from segment_stack import stack_repeated_segments
from translate_utils import translate_segments
from visual_log import show_progress_block, show_stage_complete
from start_libretranslate import ensure_libretranslate
from subtitle_io import write_srt, split_long_segments

import whisper
import argparse
import time
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)

session_dir = None

def get_session_dir() -> str:
    global session_dir
    if session_dir is None:
        session_dir = datetime.now().strftime("sessions/%Y-%m-%d_%H-%M-%S")
        os.makedirs(session_dir, exist_ok=True)
    return session_dir

def main():
    global session_dir
    parser = argparse.ArgumentParser(description="WhisperTorzokRefined v1.3.1")
    parser.add_argument("audio_path", help="Path to input audio")
    parser.add_argument("--model", default="large", help="Whisper model (base, small, medium, large)")
    parser.add_argument("--hallucination-file", help="Path to hallucination phrases file")
    args = parser.parse_args()

    ensure_libretranslate()  # Проверка и запуск LibreTranslate перед началом пайплайна
    try:
        session_dir = get_session_dir()  # фиксируем имя папки в начале
        # 🔊 Этап 1: Предобработка аудио
        show_progress_block("🧼 Audio preprocessing...", 100, {
            "speed": "simulated 120x",
            "bitrate": "1411kbit/s"
        })
        cleaned_audio = preprocess_audio(args.audio_path, session_dir)
        show_stage_complete("✅ Preprocessing complete.")

        # 🔄 Этап 2: Загрузка модели
        logging.info(f"\n🔄 Loading Whisper model: {args.model}")
        model = whisper.load_model(args.model)

        # 🗣️ Этап 3: Транскрибирование
        logging.info("\n🗣️🤖 Transcribing audio...")
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

        show_progress_block("🗣️🤖 Transcribing audio...", 100, {
            "segments": len(segments),
            "rate": f"{rate} seg/s"
        })
        show_stage_complete("✅ Transcription finished.")

        # 📜 Этап 4: Фильтрация и стакание
        hallucinations = load_hallucination_markers(args.hallucination_file)
        segments = process_segments(segments, session_dir, hallucination_markers=hallucinations)
        segments = stack_repeated_segments(segments)
        segments = split_long_segments(segments, max_chars=80)

        print("\n📜 Writing Russian subtitles...")
        write_srt(os.path.join(session_dir, "output_ru.srt"), segments)
        print(f"📁 Saved: {os.path.join(session_dir, 'output_ru.srt')}")
        print(f"📁 Repetition log: {os.path.join(session_dir, 'repetitions.log')}")

        # 🌍 Этап 5: Перевод
        print("\n🌍 Translating subtitles... [segments:", len(segments), "]")
        translated = translate_segments(segments)
        show_stage_complete("✅ Translation complete.")
        write_srt(os.path.join(session_dir, "output_en_translated.srt"), translated)
        print(f"📁 Saved: {os.path.join(session_dir, 'output_en_translated.srt')}\n")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
