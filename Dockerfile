FROM python:3.10.1-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create Tesseract directory
RUN mkdir -p /usr/share/tesseract-ocr/4.00/tessdata

# Copy Tesseract traineddata files
COPY Tesseract-OCR/tessdata/eng.traineddata /usr/share/tesseract-ocr/4.00/tessdata/
COPY poppler /app/poppler

# Verify Tesseract data
RUN ls -la /usr/share/tesseract-ocr/4.00/tessdata/

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . .

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ENV PATH="/app/poppler/poppler-24.07.0/Library/bin:${PATH}"

# Verify Tesseract installation and data
RUN tesseract --version
RUN tesseract --list-langs

EXPOSE 8501

CMD ["streamlit", "run", "app_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]