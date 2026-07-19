"""
Fase 6 — Tool Cari Web: agen yang bisa mencari info terkini di internet
=======================================================================
Sampai sekarang agenmu hanya tahu isi dokumen + kalkulator. Dengan tool ini,
agen bisa MENCARI di internet saat butuh info terbaru (berita, harga, fakta
terkini) — lalu merangkumnya beserta sumber.

Memakai DuckDuckGo: gratis, TANPA API key.

Butuh:  pip install ddgs
        .env berisi GROQ_API_KEY

Jalankan:  python cari_web.py
"""

import os
import json

from openai import OpenAI
from dotenv import load_dotenv

# Library pencarian (nama baru 'ddgs'; fallback ke nama lama bila perlu)
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)
MODEL = "llama-3.3-70b-versatile"
MODEL_CADANGAN = "llama-3.1-8b-instant"


# ============================================================
# TOOL: cari_web
# ============================================================
def cari_web(kueri, maks=5):
    """Cari di internet lewat DuckDuckGo, kembalikan judul + url + cuplikan."""
    if DDGS is None:
        return "Library pencarian belum terpasang. Jalankan: pip install ddgs"
    try:
        hasil = []
        with DDGS() as ddgs:
            for r in ddgs.text(kueri, max_results=maks):
                hasil.append({
                    "judul": r.get("title"),
                    "url": r.get("href"),
                    "cuplikan": r.get("body"),
                })
        if not hasil:
            return "Tidak ada hasil ditemukan."
        return json.dumps(hasil, ensure_ascii=False)
    except Exception as e:
        return f"Gagal mencari: {e}"


# ============================================================
# Definisi tool untuk LLM (format OpenAI/Groq)
# ============================================================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "cari_web",
            "description": (
                "Cari informasi terkini di internet. Gunakan untuk berita, harga, "
                "perkembangan terbaru, atau fakta di luar pengetahuanmu."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "kueri": {
                        "type": "string",
                        "description": "kata kunci pencarian, mis. 'harga emas hari ini'",
                    }
                },
                "required": ["kueri"],
            },
        },
    }
]
FUNGSI = {"cari_web": cari_web}

SISTEM = (
    "Kamu asisten riset Cendekia. Jika pertanyaan butuh info terkini atau di luar "
    "pengetahuanmu, panggil tool cari_web. Jawab ringkas dalam Bahasa Indonesia dan "
    "SELALU sebutkan sumber (URL) bila memakai hasil web."
)


def _chat(messages, model):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.2,
    )


# ============================================================
# Loop agen: reasoning -> panggil tool -> jawab
# ============================================================
def jalankan_agen(pertanyaan, maks_langkah=5):
    messages = [
        {"role": "system", "content": SISTEM},
        {"role": "user", "content": pertanyaan},
    ]
    for _ in range(maks_langkah):
        try:
            resp = _chat(messages, MODEL)
        except Exception as e:
            print(f"⚠️  model utama gagal ({e}); pakai cadangan...")
            resp = _chat(messages, MODEL_CADANGAN)

        pesan = resp.choices[0].message

        # Tidak ada tool call -> jawaban final
        if not pesan.tool_calls:
            return pesan.content

        # Catat pesan assistant (berisi permintaan tool)
        messages.append({
            "role": "assistant",
            "content": pesan.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in pesan.tool_calls
            ],
        })

        # Jalankan setiap tool yang diminta, kirim hasilnya balik
        for tc in pesan.tool_calls:
            nama = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            print(f"🔍 {nama}({args})")
            hasil = FUNGSI[nama](**args)
            cuplikan = str(hasil)[:120].replace("\n", " ")
            print(f"   ↳ {cuplikan}...")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(hasil),
            })

    return "Maaf, terlalu banyak langkah tanpa jawaban final."


def main():
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY belum diatur di .env")
        return
    if DDGS is None:
        print("⚠️  Library pencarian belum ada. Jalankan dulu: pip install ddgs")
        return

    print("=" * 60)
    print("  AGEN + TOOL CARI WEB — Cendekia (Fase 6)")
    print("=" * 60)
    print("Ketik pertanyaan (butuh info terkini paling terasa). 'keluar' untuk berhenti.\n")

    while True:
        try:
            pertanyaan = input("Kamu: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pertanyaan or pertanyaan.lower() in ("keluar", "exit", "quit"):
            print("Sampai jumpa! 👋")
            break
        jawaban = jalankan_agen(pertanyaan)
        print(f"\n🤖 Cendekia: {jawaban}\n")


if __name__ == "__main__":
    main()
