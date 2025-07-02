# Gunakan image dasar yang support libGL
FROM python:3.11-slim

# Install libGL dan dependensi penting
RUN apt-get update && apt-get install -y \
    libgl1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy semua file ke dalam container
COPY . /app

# Install library Python
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
