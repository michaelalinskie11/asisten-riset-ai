"""
Agen Riset Cendekia — versi AGENTIK (Fase 6)
============================================
Beda dengan RAG biasa (yang cuma: cari → jawab), agen ini bisa:
  🧠 Berpikir bertahap (multi-step reasoning)
  🔧 Memilih & memakai ALAT sendiri (tool-calling):
        • cari_dokumen : mencari jawaban di dalam dokumen (RAG)
        • hitung       : menghitung ekspresi matematika
  💬 Mengingat percakapan (memory)

Contoh pertanyaan yang butuh >1 langkah:
  "Berapa total biaya paket Profesional untuk setahun?"
  → agen cari harga di dokumen (Rp450.000), lalu HITUNG 450000 * 12.

Jalankan:  python agen.py     (ketik 'keluar' untuk berhenti)
"""
import os
import ast
import json
import operator
import numpy as np
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
JINA_KEY = os.getenv("JINA_API_KEY")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)
MODEL = "llama-3.3-70b-versatile"     # model dengan tool-calling andal
MODEL_CADANGAN = "llama-3.1-8b-instant"
TOP_K = 5

# ================= Basis pengetahuan (RAG) =================
def baca_dokumen():
    if os.path.exists("dokumen.pdf"):
        from pypdf import PdfReader
        reader = PdfReader("dokumen.pdf")
        teks = ""
        for hal in reader.pages:
            t = hal.extract_text()
            if t:
                teks += t + "\n"
        return teks
    if os.path.exists("dokumen.txt"):
        with open("dokumen.txt", encoding="utf-8") as f:
            return f.read()
    raise FileNotFoundError("Tidak menemukan dokumen.pdf atau dokumen.txt.")

def potong(teks, ukuran=500, tumpang=100):
    hasil, mulai = [], 0
    while mulai < len(teks):
        hasil.append(teks[mulai:mulai + ukuran])
        mulai += ukuran - tumpang
    return hasil

def embed(daftar_teks):
    resp = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={"Authorization": f"Bearer {JINA_KEY}"},
        json={"model": "jina-embeddings-v3", "input": daftar_teks},
    )
    resp.raise_for_status()
    return [d["embedding"] for d in resp.json()["data"]]

def kemiripan(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

CHUNKS, VECTORS = [], []

def siapkan():
    global CHUNKS, VECTORS
    teks = baca_dokumen()
    CHUNKS = potong(teks)
    VECTORS = embed(CHUNKS)

# ================= ALAT 1: cari dokumen =================
def cari_dokumen(pertanyaan):
    q = embed([pertanyaan])[0]
    skor = sorted(
        [(kemiripan(q, v), i) for i, v in enumerate(VECTORS)],
        reverse=True,
    )[:TOP_K]
    return "\n---\n".join(CHUNKS[i] for _, i in skor)

# ================= ALAT 2: kalkulator aman =================
# Hanya mengizinkan operasi aritmatika (tanpa eval() berbahaya).
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def _nilai(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_nilai(node.left), _nilai(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_nilai(node.operand))
    raise ValueError("Ekspresi tidak diizinkan")

def hitung(ekspresi):
    hasil = _nilai(ast.parse(ekspresi, mode="eval").body)
    return str(hasil)

# ================= Spesifikasi alat untuk LLM =================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "cari_dokumen",
            "description": "Cari informasi relevan di dalam dokumen yang diunggah. Gunakan untuk pertanyaan apa pun tentang isi dokumen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pertanyaan": {"type": "string", "description": "Pertanyaan atau kata kunci pencarian"}
                },
                "required": ["pertanyaan"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hitung",
            "description": "Hitung ekspresi matematika. Contoh: '450000 * 12' atau '(150000 + 450000) / 2'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ekspresi": {"type": "string", "description": "Ekspresi aritmatika yang valid"}
                },
                "required": ["ekspresi"],
            },
        },
    },
]
FUNGSI = {"cari_dokumen": cari_dokumen, "hitung": hitung}

SISTEM = """Kamu adalah Agen Riset Cendekia yang cerdas dan teliti.
Pikirkan langkah demi langkah sebelum menjawab.
- Untuk pertanyaan tentang isi dokumen, panggil alat 'cari_dokumen'.
- Untuk perhitungan angka, panggil alat 'hitung'.
- Kamu boleh memanggil beberapa alat secara berurutan (mis. cari harga dulu, lalu hitung).
- Jawab HANYA berdasarkan hasil alat. Jika informasi tidak ada di dokumen, katakan dengan jujur.
Jawab dalam Bahasa Indonesia yang jelas dan ringkas."""

# ================= Loop agen (inti tool-calling) =================
def _chat(messages):
    for model in (MODEL, MODEL_CADANGAN):
        try:
            return client.chat.completions.create(
                model=model, messages=messages, tools=TOOLS, temperature=0.2
            )
        except Exception:
            continue
    raise RuntimeError("Gagal memanggil model.")

def jalankan_agen(messages, maks_langkah=5):
    for _ in range(maks_langkah):
        resp = _chat(messages)
        msg = resp.choices[0].message

        # Tidak ada panggilan alat -> ini jawaban final
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content

        # Catat niat memanggil alat
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })

        # Jalankan setiap alat, kembalikan hasilnya ke model
        for tc in msg.tool_calls:
            nama = tc.function.name
            args = {}
            try:
                args = json.loads(tc.function.arguments)
                hasil = FUNGSI[nama](**args)
            except Exception as e:
                hasil = f"Error: {e}"
            cuplikan = str(hasil).replace("\n", " ")[:70]
            print(f"   🔧 alat '{nama}' {args} → {cuplikan}...")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(hasil),
            })
    return "Maaf, terlalu banyak langkah tanpa jawaban akhir."

# ================= Program utama =================
def main():
    if not JINA_KEY or not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY / JINA_API_KEY belum ada di .env")
        return

    print("📚 Menyiapkan basis pengetahuan...")
    siapkan()
    print(f"   {len(CHUNKS)} potongan siap.\n")
    print("✦ Agen Riset Cendekia siap. Ketik pertanyaan (atau 'keluar').")
    print("  Coba: 'Berapa total biaya paket Profesional untuk setahun?'\n")

    messages = [{"role": "system", "content": SISTEM}]
    while True:
        try:
            q = input("❓ Kamu: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("keluar", "exit", "quit", ""):
            break
        messages.append({"role": "user", "content": q})
        jawaban = jalankan_agen(messages)
        print(f"\n✦ Cendekia: {jawaban}\n")

    print("\nSampai jumpa! 👋")

if __name__ == "__main__":
    main()
