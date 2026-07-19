"""
Fase 5 — Keandalan Produksi: Caching + Fallback antar-model
===========================================================
Dua teknik yang membuat aplikasi AI-mu HEMAT & TAHAN BANTING seperti produk sungguhan:

1) CACHING  — simpan jawaban berdasarkan 'sidik jari' (hash) input.
              Pertanyaan sama ditanya lagi? Jawab instan, 0 biaya API.
2) FALLBACK — kalau model utama error / kena limit, otomatis pindah ke model cadangan.
              Aplikasi tetap hidup meski satu model bermasalah.

Jalankan:  python keandalan.py
"""

import os
import json
import time
import hashlib

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

MODEL_UTAMA = "llama-3.3-70b-versatile"
MODEL_CADANGAN = "llama-3.1-8b-instant"
CACHE_FILE = "cache.json"


# ============================================================
# CACHE sederhana berbasis file JSON
# ============================================================
def _muat_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _simpan_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


_CACHE = _muat_cache()


def _kunci(*bagian):
    """Buat 'sidik jari' unik dari input — input sama => kunci sama."""
    gabung = "||".join(map(str, bagian))
    return hashlib.sha256(gabung.encode("utf-8")).hexdigest()[:16]


# ============================================================
# CHAT dengan cache + fallback
# ============================================================
def tanya(prompt, gunakan_cache=True):
    kunci = _kunci("chat", prompt)

    # 1) Cek cache dulu
    if gunakan_cache and kunci in _CACHE:
        print("⚡ (dari cache — instan, 0 biaya API)")
        return _CACHE[kunci]["jawaban"]

    # 2) Coba model utama, lalu cadangan (fallback)
    galat_terakhir = None
    for model in (MODEL_UTAMA, MODEL_CADANGAN):
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            jawaban = resp.choices[0].message.content
            durasi = time.time() - t0
            print(f"🤖 model dipakai: {model}  ({durasi:.1f}s)")

            # 3) Simpan ke cache
            _CACHE[kunci] = {"model": model, "jawaban": jawaban}
            _simpan_cache(_CACHE)
            return jawaban
        except Exception as e:
            galat_terakhir = e
            print(f"⚠️  {model} gagal ({e}); mencoba model cadangan...")

    raise RuntimeError(f"Semua model gagal. Galat terakhir: {galat_terakhir}")


def main():
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY belum diatur di .env")
        return

    print("=" * 60)
    print("  KEANDALAN: CACHING + FALLBACK — Cendekia (Fase 5)")
    print("=" * 60)

    pertanyaan = "Jelaskan apa itu RAG dalam 2 kalimat sederhana."

    print("\n▶️  Panggilan PERTAMA (memanggil API):")
    t0 = time.time()
    jawab1 = tanya(pertanyaan)
    print(f"   ⏱️  total {time.time() - t0:.2f}s")
    print(f"   💬 {jawab1}")

    print("\n▶️  Panggilan KEDUA (pertanyaan sama — harusnya dari cache):")
    t0 = time.time()
    jawab2 = tanya(pertanyaan)
    print(f"   ⏱️  total {time.time() - t0:.2f}s  ← bandingkan kecepatannya!")
    print(f"   💬 {jawab2}")

    print("\n💡 Cache tersimpan di", CACHE_FILE, "— tambahkan ke .gitignore agar tidak ikut ter-commit.")


if __name__ == "__main__":
    main()
