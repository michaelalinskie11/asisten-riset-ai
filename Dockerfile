# Resep build untuk Hugging Face Spaces (Docker)
FROM python:3.11-slim

WORKDIR /app

# Pasang bahan lebih dulu (biar cache build efisien)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin sisa kode (main.py, dll.)
COPY . .

# Hugging Face Spaces mengharapkan aplikasi berjalan di port 7860
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
