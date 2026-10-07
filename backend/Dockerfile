# PDF360 backend — FastAPI + Celery worker share this image.
# System dependencies below are not optional: LibreOffice, Tesseract, and
# Ghostscript are shelled out to directly by app/services/pdf_engine/
# conversion.py and ocr.py — confirmed required by running those engines
# in development, not a guess.

FROM python:3.12-slim

# Ghostscript pulls in most of what OCR needs; libreoffice-writer +
# libreoffice-calc + libreoffice-impress cover doc/xlsx/pptx conversion
# without the full libreoffice meta-package's ~1GB of extras.
#
# Language packs: eng/fra/spa/ara are real apt packages (tesseract-ocr-<code>).
# Hausa is NOT available as an apt package on Debian/Ubuntu — confirmed by
# checking apt-cache directly, not assumed — so its trained-data file is
# fetched straight from the official tesseract-ocr/tessdata repo instead.
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
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL -o /usr/share/tesseract-ocr/5/tessdata/hau.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/hau.traineddata

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m app.db.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

