FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip git curl ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages libretranslate argostranslate

ENV PATH="/root/.local/bin:/usr/local/bin:${PATH}"

# 📥 Копируем скрипт и запускаем установку моделей
COPY install_models.py /opt/install_models.py
RUN python3 /opt/install_models.py

CMD ["libretranslate", "--host", "0.0.0.0", "--port", "5000"]
