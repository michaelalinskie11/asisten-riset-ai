# Cendekia — Backend Production-Grade (Tier 2)

Paket ini bikin backend siap-deploy: Docker, testing, CI/CD, dan validasi konfigurasi.
Letakkan semua file ini di **root repo backend** (sejajar dengan `main.py`).

## Isi paket
| File | Fungsi |
|------|--------|
| `Dockerfile` | Bungkus API jadi image (dipakai Railway/Fly/lokal) |
| `.dockerignore` | Biar image ramping (skip venv, .env, dll) |
| `docker-compose.yml` | Jalankan API lokal 1 perintah + healthcheck |
| `.env.example` | Template semua env var wajib |
| `konfigurasi.py` | Validasi env var saat startup |
| `pytest.ini` + `tests/` | Smoke test API |
| `requirements-dev.txt` | Dependensi test/lint |
| `.github/workflows/ci.yml` | CI otomatis tiap push ke main |

## Langkah pakai

### 1. Siapkan env
```bash
cp .env.example .env   # lalu isi nilai aslinya
```

### 2. Aktifkan validasi konfigurasi
Di `main.py`, setelah `load_dotenv()`, tambahkan:
```python
from konfigurasi import validasi_env
validasi_env()
```

### 3. Lengkapi requirements.txt
Pastikan ada (yang sempat tertinggal):
```
psycopg2-binary
ddgs
```

### 4. Jalankan lewat Docker (lokal)
```bash
docker compose up --build
# API -> http://localhost:8000/docs
```

### 5. Jalankan test
```bash
pip install -r requirements-dev.txt
pytest -q
```

### 6. Aktifkan CI/CD
File `.github/workflows/ci.yml` otomatis jalan tiap `git push` ke `main`
(install deps -> lint ruff -> pytest). Cek tab **Actions** di GitHub.

## Setelah ini
Tier 2 selesai -> lanjut **deploy ke production** (backend ke Railway/Fly pakai Dockerfile ini,
frontend ke Vercel), lalu poles frontend (routing + fitur).
