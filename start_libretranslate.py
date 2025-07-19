# Запуск локального сервера LibreTranslate через Docker Compose

import subprocess
import logging
import os

def start_libretranslate_stack():
    """
    Запускает LibreTranslate и Traefik через docker-compose, если они ещё не запущены.
    """
    compose_dir = os.path.join(os.path.dirname(__file__), 'libretranslate-stack')
    try:
        result = subprocess.run([
            'docker-compose', 'up', '-d'
        ], cwd=compose_dir, capture_output=True, text=True, check=True)
        logging.info("LibreTranslate stack started (docker-compose up -d)")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start LibreTranslate stack: {e.stderr}")
        raise

def is_libretranslate_running() -> bool:
    """
    Проверяет, доступен ли сервис LibreTranslate по адресу http://translate.localhost/translate
    """
    import requests
    try:
        resp = requests.post("http://translate.localhost/translate", timeout=2)
        return resp.status_code in (200, 400)  # 400 если не передан текст
    except Exception:
        return False

def ensure_libretranslate():
    """
    Запускает LibreTranslate через docker-compose, если сервис не отвечает.
    """
    if not is_libretranslate_running():
        start_libretranslate_stack()
        import time
        for _ in range(20):
            if is_libretranslate_running():
                logging.info("LibreTranslate is up!")
                return
            time.sleep(1)
        raise RuntimeError("LibreTranslate did not start in time.")
    else:
        logging.info("LibreTranslate already running.")

if __name__ == "__main__":
    ensure_libretranslate()
