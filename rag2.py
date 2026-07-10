import os
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

# ---------- 1. BACA PDF ----------
reader = PdfReader("dokumen.pdf")
teks = ""
for halaman in reader.pages:
    t = halaman.extract_text()
    if t:
        teks += t + "\n"
print("PDF terbaca:", len(teks), "karakter")

# ---------- 2. CHUNKING: potong jadi bagian kecil ----------
def potong(teks, ukuran=500, tumpang=100):
    hasil, mulai = [], 0
    while mulai < len(teks):
        hasil.append(teks[mulai:mulai + ukuran])
        mulai += ukuran - tumpang   # tumpang-tindih biar konteks tak terpotong
    return hasil

chunks = potong(teks)
print("Dokumen dipotong jadi", len(chunks), "bagian")

# ---------- 3. EMBEDDING via Jina ----------
def embed(daftar_teks):
    resp = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={"Authorization": f"Bearer {JINA_KEY}"},
        json={"model": "jina-embeddings-v3", "input": daftar_teks},
    )
    resp.raise_for_status()
    return [d["embedding"] for d in resp.json()["data"]]

print("Membuat embedding semua bagian (sekali saja)...")
chunk_vectors = embed(chunks)

# ---------- 4. Ukur kedekatan makna (cosine similarity) ----------
def kemiripan(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ---------- 5. Tanya-jawab ----------
print("\nSiap! Ketik 'keluar' untuk berhenti.\n")
while True:
    pertanyaan = input("Tanya: ")
    if pertanyaan.lower() == "keluar":
        break

    q_vec = embed([pertanyaan])[0]                      # koordinat pertanyaan

    # skor tiap bagian, ambil 3 paling relevan
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
    print("\nJawaban:", resp.choices[0].message.content)
    print("(diambil dari bagian nomor:", [i for _, i in top], ")\n")