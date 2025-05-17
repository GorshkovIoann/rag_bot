# Dockerfile

# Используем CUDA runtime для запуска на GPU
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установим базовые утилиты и Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    tesseract-ocr tesseract-ocr-rus \
    poppler-utils libgl1 libsm6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем их
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt python-dotenv

# Скачиваем punkt
RUN python3 - <<EOF
import nltk; nltk.download('punkt')
EOF

# Копируем весь код
COPY . .

# Создаём папку для данных
RUN mkdir -p data

CMD ["python3", "bot.py"]
