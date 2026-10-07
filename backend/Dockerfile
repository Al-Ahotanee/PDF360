# PDF360 backend — FastAPI + Celery worker in a unified free-tier image.
# System dependencies below are not optional: LibreOffice, Tesseract, and
# Ghostscript are shelled out to directly by app/services/pdf_engine/
# conversion.py and ocr.py — confirmed required by running those engines
# in development, not a guess.

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    tesseract-ocr-ara \
    ghostscript \
    poppler-utils \
    curl \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL -o /usr/share/tesseract-ocr/5/tessdata/hau.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/hau.traineddata

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage && chmod +x /app/start.sh

EXPOSE 8000

CMD ["./start.sh"]
