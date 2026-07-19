"""Smoke test dasar untuk API Cendekia.

Prinsip: test TIDAK menyentuh layanan eksternal (Qdrant/Supabase/Groq),
supaya cepat & selalu stabil di CI. Kita cukup memverifikasi aplikasinya
bisa diimport, rute pentingnya terpasang, dan skema OpenAPI valid.
"""

import os

# Env dummy supaya import main & validasi konfigurasi tidak gagal.
os.environ.setdefault("GROQ_API_KEY", "test")
os.environ.setdefault("JINA_API_KEY", "test")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_API_KEY", "test")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("API_KEY", "test")

from main import app  # noqa: E402


def test_konfigurasi_wajib():
    from konfigurasi import WAJIB

    assert "GROQ_API_KEY" in WAJIB
    assert "API_KEY" in WAJIB


def test_app_punya_rute_penting():
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/health" in paths
    assert "/tanya" in paths


def test_openapi_valid():
    skema = app.openapi()
    assert skema["info"]["title"]
    assert "/health" in skema["paths"]
