FROM python:3.10.1-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV POPPLER_PATH=/usr/bin

EXPOSE 8501

CMD ["streamlit", "run", "app_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]