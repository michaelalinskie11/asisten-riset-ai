import os
import json
import numpy as np
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
JINA_KEY = os.getenv("JINA_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

CACHE_FILE = "embeddings.json"

def embed(daftar_teks):
    resp = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={"Authorization": f"Bearer {JINA_KEY}"},
        json={"model": "jina-embeddings-v3", "input": daftar_teks},
    )
    resp.raise_for_status()
    return [d["embedding"] for d in resp.json()["data"]]

def potong(teks, ukuran=500, tumpang=100):
    hasil, mulai = [], 0
    while mulai < len(teks):
        hasil.append(teks[mulai:mulai + ukuran])
        mulai += ukuran - tumpang
    return hasil

# ---------- Muat cache kalau ada; kalau belum, buat lalu simpan ----------
if os.path.exists(CACHE_FILE):
    print("⚡ Memuat embeddings dari cache (cepat)...")
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    chunks, chunk_vectors = data["chunks"], data["vectors"]
else:
    print("🔧 Cache belum ada. Membaca PDF & membuat embeddings (sekali saja)...")
    reader = PdfReader("dokumen.pdf")
    teks = ""
    for halaman in reader.pages:
        t = halaman.extract_text()
        if t:
            teks += t + "\n"
    chunks = potong(teks)
    chunk_vectors = embed(chunks)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"chunks": chunks, "vectors": chunk_vectors}, f)
    print("💾 Embeddings disimpan ke", CACHE_FILE)

print("Total bagian:", len(chunks))

def kemiripan(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ---------- Tanya-jawab ----------
print("\nSiap! Ketik 'keluar' untuk berhenti.\n")
while True:
    pertanyaan = input("Tanya: ")
    if pertanyaan.lower() == "keluar":
        break

    q_vec = embed([pertanyaan])[0]
    skor = sorted(
        [(kemiripan(q_vec, v), i) for i, v in enumerate(chunk_vectors)],
        reverse=True,
    )
    top = skor[:3]
    konteks = "\n---\n".join(chunks[i] for _, i in top)

    prompt = f"""Jawab pertanyaan HANYA berdasarkan konteks di bawah.
Jika tidak ada, katakan "Tidak ada di dokumen."

KONTEKS:
{konteks}

Pertanyaan: {pertanyaan}
"""
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    print("\n💬 Jawaban:", resp.choices[0].message.content)

    # 📌 Tampilkan SUMBER yang dipakai
    print("\n📌 Sumber yang digunakan:")
    for nilai, i in top:
        cuplikan = chunks[i].replace("\n", " ").strip()[:120]
        print(f"  [bagian {i} | kemiripan {nilai:.2f}] {cuplikan}...")
    print()