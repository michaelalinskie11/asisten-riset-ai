# =====================================================
#  main.py — Backend API Cendekia (FastAPI + Qdrant)
#  Fase 4: siap-deploy. Qdrant otomatis pilih Cloud (kalau
#          QDRANT_URL di-set) atau lokal (untuk ngoding).
#
#  Endpoint:  /health  /upload  /tanya
#  Lokal:  python -m uvicorn main:app --reload
#  Server: uvicorn main:app --host 0.0.0.0 --port $PORT
#  Dok:    http://127.0.0.1:8000/docs
# =====================================================
import os
import io
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")            # kosong = pakai Qdrant lokal
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
MODEL = "llama-3.1-8b-instant"
EMBED_MODEL = "jina-embeddings-v3"
COLLECTION = "cendekia"

# --- Klien Groq (library openai, tukar base_url) ---
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# --- Vector database Qdrant: Cloud kalau ada QDRANT_URL, kalau tidak lokal ---
if QDRANT_URL:
    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("Qdrant: mode CLOUD")
else:
    qdrant = QdrantClient(path="./qdrant_data")
    print("Qdrant: mode LOKAL")


# ---------- Fungsi bantu ----------
def potong(teks: str, ukuran: int = 500, tumpang: int = 100):
    hasil = []
    mulai = 0
    while mulai < len(teks):
        hasil.append(teks[mulai:mulai + ukuran])
        mulai += ukuran - tumpang
    return [p for p in hasil if p.strip()]


def embed_banyak(list_teks):
    resp = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"model": EMBED_MODEL, "input": list_teks},
        timeout=60,
    )
    resp.raise_for_status()
    return [d["embedding"] for d in resp.json()["data"]]


def embed_satu(teks: str):
    return embed_banyak([teks])[0]


def simpan_ke_qdrant(potongan, vektor):
    dim = len(vektor[0])
    if qdrant.collection_exists(COLLECTION):
        qdrant.delete_collection(COLLECTION)
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    points = [
        PointStruct(id=i, vector=vektor[i], payload={"teks": potongan[i]})
        for i in range(len(potongan))
    ]
    qdrant.upsert(collection_name=COLLECTION, points=points)


def cari_konteks(pertanyaan: str, k: int = 3):
    q = embed_satu(pertanyaan)
    hasil = qdrant.query_points(
        collection_name=COLLECTION, query=q, limit=k
    ).points
    return [h.payload["teks"] for h in hasil]


# ===================== FastAPI =====================
app = FastAPI(title="Cendekia API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pertanyaan(BaseModel):
    pertanyaan: str


@app.get("/health")
def health():
    jumlah = 0
    if qdrant.collection_exists(COLLECTION):
        jumlah = qdrant.count(collection_name=COLLECTION).count
    mode = "cloud" if QDRANT_URL else "lokal"
    return {"status": "ok", "database": f"qdrant ({mode})", "jumlah_potongan": jumlah}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    isi = await file.read()
    try:
        reader = PdfReader(io.BytesIO(isi))
        teks = "\n".join((hal.extract_text() or "") for hal in reader.pages)
    except Exception as e:
        return {"status": "error", "pesan": f"Gagal membaca PDF: {e}"}

    if not teks.strip():
        return {
            "status": "error",
            "pesan": "PDF tidak berisi teks yang bisa dibaca (mungkin hasil scan/gambar).",
        }

    potongan = potong(teks)
    vektor = embed_banyak(potongan)
    simpan_ke_qdrant(potongan, vektor)

    return {
        "status": "ok",
        "nama_file": file.filename,
        "jumlah_potongan": len(potongan),
        "pesan": "Dokumen berhasil diindeks. Silakan bertanya di /tanya.",
    }


@app.post("/tanya")
def tanya(body: Pertanyaan):
    konteks = cari_konteks(body.pertanyaan)
    konteks_teks = "\n\n".join(f"[{i+1}] {c}" for i, c in enumerate(konteks))

    prompt = (
        "Kamu adalah Cendekia, asisten riset dokumen. "
        "Jawab pertanyaan HANYA berdasarkan konteks di bawah. "
        "Jika jawabannya tidak ada di konteks, katakan dengan jujur bahwa "
        "informasi itu tidak ditemukan dalam dokumen.\n\n"
        f"Konteks:\n{konteks_teks}\n\n"
        f"Pertanyaan: {body.pertanyaan}\n"
        "Jawaban:"
    )

    def stream():
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            stream=True,
        )
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")
