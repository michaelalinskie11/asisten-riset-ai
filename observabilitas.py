"""
Fase 5 — Observability: logging, tracing & monitoring biaya token
=================================================================
"Kalau tidak bisa kamu ukur, tidak bisa kamu perbaiki."
Modul ini mencatat SETIAP panggilan LLM: model, waktu, jumlah token, dan estimasi
biaya — lalu menyimpannya ke jejak.jsonl. Persis yang dilakukan tool seperti
Langfuse, tapi versi lokal & nol biaya untuk memahami konsepnya.

Jalankan:  python observabilitas.py
"""

import os
import json
import time
import datetime

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

JEJAK_FILE = "jejak.jsonl"

# Harga per 1 JUTA token (USD) — perkiraan Groq; sesuaikan bila berubah.
# Format: model -> (harga_input, harga_output)
HARGA = {
    "llama-3.1-8b-instant": (0.05, 0.08),
    "llama-3.3-70b-versatile": (0.59, 0.79),
}


def _hitung_biaya(model, token_input, token_output):
    masuk, keluar = HARGA.get(model, (0.0, 0.0))
    return (token_input / 1_000_000) * masuk + (token_output / 1_000_000) * keluar


def lacak_chat(model, messages, **kwargs):
    """Bungkus panggilan chat: jalankan, ukur, catat ke jejak.jsonl, kembalikan respons."""
    t0 = time.time()
    galat = None
    resp = None
    try:
        resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
        return resp
    except Exception as e:
        galat = str(e)
        raise
    finally:
        durasi = round(time.time() - t0, 3)
        u = getattr(resp, "usage", None) if resp else None
        tok_in = getattr(u, "prompt_tokens", 0) if u else 0
        tok_out = getattr(u, "completion_tokens", 0) if u else 0
        catatan = {
            "waktu": datetime.datetime.now().isoformat(timespec="seconds"),
            "model": model,
            "latency_dtk": durasi,
            "token_input": tok_in,
            "token_output": tok_out,
            "token_total": tok_in + tok_out,
            "biaya_usd": round(_hitung_biaya(model, tok_in, tok_out), 8),
            "galat": galat,
        }
        with open(JEJAK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(catatan, ensure_ascii=False) + "\n")
        status = "✅" if not galat else "❌"
        print(f"   {status} [{model}] {durasi}s · {tok_in + tok_out} token · ${catatan['biaya_usd']:.6f}")


def ringkasan():
    """Baca jejak.jsonl dan tampilkan agregat: total panggilan, token, biaya, rata-rata latency."""
    if not os.path.exists(JEJAK_FILE):
        print("Belum ada jejak.")
        return
    baris = [json.loads(x) for x in open(JEJAK_FILE, encoding="utf-8") if x.strip()]
    if not baris:
        print("Belum ada jejak.")
        return

    total_panggilan = len(baris)
    total_token = sum(b["token_total"] for b in baris)
    total_biaya = sum(b["biaya_usd"] for b in baris)
    rata_latency = sum(b["latency_dtk"] for b in baris) / total_panggilan
    gagal = sum(1 for b in baris if b.get("galat"))

    print("\n" + "=" * 60)
    print("  RINGKASAN OBSERVABILITY")
    print("=" * 60)
    print(f"📞 Total panggilan : {total_panggilan}  (gagal: {gagal})")
    print(f"🧮 Total token     : {total_token:,}")
    print(f"💰 Total biaya     : ${total_biaya:.6f}")
    print(f"⏱️  Rata latency    : {rata_latency:.2f}s")

    # Rincian per model
    per_model = {}
    for b in baris:
        m = per_model.setdefault(b["model"], {"n": 0, "token": 0, "biaya": 0.0})
        m["n"] += 1
        m["token"] += b["token_total"]
        m["biaya"] += b["biaya_usd"]
    print("\nPer model:")
    for m, s in per_model.items():
        print(f"   • {m}: {s['n']} panggilan · {s['token']:,} token · ${s['biaya']:.6f}")


def main():
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY belum diatur di .env")
        return

    print("=" * 60)
    print("  OBSERVABILITY — Cendekia (Fase 5)")
    print("=" * 60)

    print("\n▶️  Beberapa panggilan contoh (otomatis tercatat):")
    contoh = [
        ("llama-3.1-8b-instant", "Apa itu embedding? Jawab 1 kalimat."),
        ("llama-3.3-70b-versatile", "Sebutkan 3 manfaat RAG secara singkat."),
        ("llama-3.1-8b-instant", "Apa bedanya cache dan database? 1 kalimat."),
    ]
    for model, prompt in contoh:
        resp = lacak_chat(model, [{"role": "user", "content": prompt}], temperature=0.2)
        print(f"      ↳ {resp.choices[0].message.content.strip()[:80]}...")

    ringkasan()
    print("\n💡 Semua jejak tersimpan di", JEJAK_FILE, "— tambahkan ke .gitignore.")


if __name__ == "__main__":
    main()
