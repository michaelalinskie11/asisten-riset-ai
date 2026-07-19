"""Validasi environment variable saat startup.

Cara pakai: di baris paling atas main.py (setelah load_dotenv), tambahkan:

    from konfigurasi import validasi_env
    validasi_env()

Kalau ada env wajib yang kosong, server berhenti dengan pesan jelas
daripada error misterius di tengah request.
"""

import os
import sys

WAJIB = [
    "GROQ_API_KEY",
    "JINA_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "DATABASE_URL",
    "API_KEY",
]


def validasi_env() -> None:
    hilang = [k for k in WAJIB if not os.getenv(k)]
    if hilang:
        print(
            "[KONFIGURASI] Environment variable wajib belum diisi: "
            + ", ".join(hilang),
            file=sys.stderr,
        )
        print(
            "[KONFIGURASI] Salin .env.example -> .env lalu lengkapi nilainya.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print("[KONFIGURASI] Semua environment variable wajib terisi.")
