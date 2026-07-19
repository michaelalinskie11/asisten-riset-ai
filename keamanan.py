"""
Fase 3 — Keamanan API: Autentikasi (API Key) + Rate Limiting
============================================================
Dua lapis pelindung backend produksi:
1) AUTENTIKASI  — hanya request dengan API key benar yang boleh masuk.
2) RATE LIMITING — batasi jumlah request per menit agar tidak disalahgunakan/boros biaya.

Butuh:  pip install fastapi uvicorn
        .env berisi  API_KEY=rahasia-kamu

Jalankan:  uvicorn keamanan:app --reload
Tes UI  :  buka http://127.0.0.1:8000/docs
"""

import os
import time
from collections import defaultdict, deque

from fastapi import FastAPI, Depends, Header, HTTPException, Request
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY", "rahasia123")

# Rate limit: maksimal 5 request per 60 detik per klien
BATAS = 5
JENDELA = 60  # detik
_riwayat = defaultdict(deque)  # kunci_klien -> deque[timestamp]

app = FastAPI(title="Cendekia API — Keamanan")


def verifikasi_kunci(x_api_key: str = Header(None)):
    """Dependency: pastikan header X-API-Key benar."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key salah atau tidak ada.")
    return x_api_key


def batasi_laju(request: Request, x_api_key: str = Header(None)):
    """Dependency: tolak bila request melebihi BATAS dalam JENDELA detik."""
    kunci = x_api_key or (request.client.host if request.client else "tanpa-ip")
    sekarang = time.time()
    antrian = _riwayat[kunci]
    # buang timestamp yang sudah keluar dari jendela waktu
    while antrian and sekarang - antrian[0] > JENDELA:
        antrian.popleft()
    if len(antrian) >= BATAS:
        sisa = int(JENDELA - (sekarang - antrian[0]))
        raise HTTPException(
            status_code=429,
            detail=f"Terlalu banyak request. Coba lagi dalam {sisa} detik.",
        )
    antrian.append(sekarang)


@app.get("/")
def publik():
    """Endpoint publik — bebas diakses siapa saja."""
    return {"pesan": "Endpoint publik. Coba akses /rahasia dengan API key."}


@app.get("/rahasia", dependencies=[Depends(batasi_laju)])
def rahasia(kunci: str = Depends(verifikasi_kunci)):
    """Endpoint terlindungi: butuh API key benar DAN belum kena rate limit."""
    return {
        "pesan": "✅ Berhasil! Kamu lolos autentikasi & rate limit.",
        "batas_per_menit": BATAS,
    }
