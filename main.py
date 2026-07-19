# =====================================================
#  main.py — Backend PRODUKSI Cendekia (v5)
#  Menyatukan seluruh fitur kelas industri jadi satu sistem hidup:
#    • RAG (Qdrant + Jina + Groq) dengan jawaban streaming
#    • Caching  — pertanyaan sama = jawab instan, 0 biaya API
#    • Fallback — model utama gagal? otomatis pindah ke cadangan
#    • Observability — catat model, latency, token & biaya tiap panggilan
#    • Rate limiting — lindungi backend dari penyalahgunaan
#    • Multi-dokumen — simpan & kelola banyak dokumen sekaligus
#    • Riwayat — tersimpan permanen ke PostgreSQL (opsional, graceful)
#    • Logging & error handling rapi
#
#  Lokal:  python -m uvicorn main:app --reload
#  Server: uvicorn main:app --host 0.0.0.0 --port $PORT
#  Dok:    http://127.0.0.1:8000/docs
# =====================================================
import os
import io
import json
import time
import uuid
import base64
import hashlib
import logging
import datetime
from collections import defaultdict, deque

import requests
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    FilterSelector,
)

# psycopg2 opsional: kalau tidak ada / DATABASE_URL kosong, app tetap jalan
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    _ADA_PSYCOPG2 = True
except ImportError:
    _ADA_PSYCOPG2 = False

load_dotenv()

from konfigurasi import validasi_env
validasi_env()
# ---------------- Logging terstruktur ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("cendekia")

# ---------------- Konfigurasi ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

MODEL_UTAMA = "llama-3.1-8b-instant"
MODEL_CADANGAN = "llama-3.3-70b-versatile"
EMBED_MODEL = "jina-embeddings-v3"
COLLECTION = "cendekia"
DIM = 1024  # dimensi embedding Jina v3

CACHE_FILE = "cache.json"
JEJAK_FILE = "jejak.jsonl"

# Harga per 1 JUTA token (USD) — perkiraan Groq: model -> (input, output)
HARGA = {
    "llama-3.1-8b-instant": (0.05, 0.08),
    "llama-3.3-70b-versatile": (0.59, 0.79),
}

# Rate limit: maksimal BATAS request per JENDELA detik per klien (IP)
BATAS = 30
JENDELA = 60
_kunjungan = defaultdict(deque)

# ---------------- Klien eksternal ----------------
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

if QDRANT_URL:
    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
else:
    qdrant = QdrantClient(path="./qdrant_data")


# ============================================================
#  CACHE (berbasis file JSON)
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
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.warning("Gagal menyimpan cache: %s", e)


_CACHE = _muat_cache()


def _kunci(*bagian):
    gabung = "||".join(map(str, bagian))
    return hashlib.sha256(gabung.encode("utf-8")).hexdigest()[:16]


# ============================================================
#  OBSERVABILITY (jejak.jsonl)
# ============================================================
def _hitung_biaya(model, tok_in, tok_out):
    masuk, keluar = HARGA.get(model, (0.0, 0.0))
    return (tok_in / 1_000_000) * masuk + (tok_out / 1_000_000) * keluar


def _catat_jejak(model, latency, tok_in, tok_out, cache_hit=False, galat=None):
    catatan = {
        "waktu": datetime.datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "latency_dtk": latency,
        "token_input": tok_in,
        "token_output": tok_out,
        "token_total": tok_in + tok_out,
        "biaya_usd": round(_hitung_biaya(model, tok_in, tok_out), 8),
        "cache_hit": cache_hit,
        "galat": galat,
    }
    try:
        with open(JEJAK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(catatan, ensure_ascii=False) + "\n")
    except Exception as e:
        log.warning("Gagal menulis jejak: %s", e)
    tanda = "⚡cache" if cache_hit else model
    log.info("tanya · %s · %ss · %s token · $%.6f",
             tanda, latency, tok_in + tok_out, catatan["biaya_usd"])


# ============================================================
#  DATABASE (PostgreSQL) — opsional & graceful
# ============================================================
def _db_aktif():
    return bool(DATABASE_URL and _ADA_PSYCOPG2)


def _koneksi():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    try:
        with _koneksi() as conn, conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS riwayat (
                    id SERIAL PRIMARY KEY,
                    pertanyaan TEXT NOT NULL,
                    jawaban TEXT NOT NULL,
                    dibuat TIMESTAMPTZ DEFAULT now()
                );"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS dokumen (
                    id SERIAL PRIMARY KEY,
                    nama TEXT NOT NULL,
                    jumlah_potongan INTEGER DEFAULT 0,
                    dibuat TIMESTAMPTZ DEFAULT now()
                );"""
            )
            conn.commit()
        log.info("Database PostgreSQL siap (tabel riwayat & dokumen).")
    except Exception as e:
        log.warning("Gagal inisialisasi database: %s", e)


def simpan_riwayat(pertanyaan, jawaban):
    if not _db_aktif():
        return
    try:
        with _koneksi() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO riwayat (pertanyaan, jawaban) VALUES (%s, %s);",
                (pertanyaan, jawaban),
            )
            conn.commit()
    except Exception as e:
        log.warning("Gagal menyimpan riwayat: %s", e)


def catat_dokumen_db(nama, jumlah):
    if not _db_aktif():
        return
    try:
        with _koneksi() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO dokumen (nama, jumlah_potongan) VALUES (%s, %s);",
                (nama, jumlah),
            )
            conn.commit()
    except Exception as e:
        log.warning("Gagal menyimpan catatan dokumen: %s", e)


def ambil_riwayat(limit=20):
    if not _db_aktif():
        return []
    try:
        with _koneksi() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, pertanyaan, jawaban, dibuat FROM riwayat "
                "ORDER BY dibuat DESC LIMIT %s;",
                (limit,),
            )
            rows = cur.fetchall()
        for r in rows:
            if r.get("dibuat"):
                r["dibuat"] = r["dibuat"].isoformat()
        return rows
    except Exception as e:
        log.warning("Gagal mengambil riwayat: %s", e)
        return []


# ============================================================
#  RAG: chunking, embedding, Qdrant (multi-dokumen)
# ============================================================
def potong(teks, ukuran=500, tumpang=100):
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


def embed_satu(teks):
    return embed_banyak([teks])[0]


def _pastikan_koleksi(dim=DIM):
    if not qdrant.collection_exists(COLLECTION):
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def simpan_ke_qdrant(potongan, vektor, nama_file, doc_id):
    """Multi-dokumen: TAMBAH potongan baru tanpa menghapus dokumen lain."""
    _pastikan_koleksi(len(vektor[0]))
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vektor[i],
            payload={"teks": potongan[i], "nama_file": nama_file, "doc_id": doc_id},
        )
        for i in range(len(potongan))
    ]
    qdrant.upsert(collection_name=COLLECTION, points=points)


def cari_konteks(pertanyaan, k=3):
    if not qdrant.collection_exists(COLLECTION):
        return []
    q = embed_satu(pertanyaan)
    hasil = qdrant.query_points(collection_name=COLLECTION, query=q, limit=k).points
    return [
        {"teks": h.payload.get("teks", ""), "nama_file": h.payload.get("nama_file", "")}
        for h in hasil
    ]


def daftar_dokumen():
    """Kelompokkan seluruh potongan menjadi daftar dokumen unik."""
    if not qdrant.collection_exists(COLLECTION):
        return []
    docs = {}
    offset = None
    while True:
        points, offset = qdrant.scroll(
            collection_name=COLLECTION,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for p in points:
            did = p.payload.get("doc_id", "lama")
            d = docs.setdefault(
                did,
                {"doc_id": did,
                 "nama_file": p.payload.get("nama_file", "(dokumen lama)"),
                 "jumlah_potongan": 0},
            )
            d["jumlah_potongan"] += 1
        if offset is None:
            break
    return list(docs.values())


def hapus_dokumen(doc_id):
    qdrant.delete(
        collection_name=COLLECTION,
        points_selector=FilterSelector(
            filter=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            )
        ),
    )


# ============================================================
#  RATE LIMITING
# ============================================================
def batasi_laju(request: Request):
    kunci = request.client.host if request.client else "tanpa-ip"
    sekarang = time.time()
    antrian = _kunjungan[kunci]
    while antrian and sekarang - antrian[0] > JENDELA:
        antrian.popleft()
    if len(antrian) >= BATAS:
        sisa = int(JENDELA - (sekarang - antrian[0]))
        raise HTTPException(
            status_code=429,
            detail=f"Terlalu banyak permintaan. Coba lagi dalam {sisa} detik.",
        )
    antrian.append(sekarang)


# ===================== FastAPI =====================
app = FastAPI(title="Cendekia API", version="5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Sumber"],
)


class Pertanyaan(BaseModel):
    pertanyaan: str


@app.on_event("startup")
def _mulai():
    log.info("Qdrant: mode %s", "CLOUD" if QDRANT_URL else "LOKAL")
    if not GROQ_API_KEY:
        log.warning("GROQ_API_KEY belum diatur di .env")
    if not JINA_API_KEY:
        log.warning("JINA_API_KEY belum diatur di .env")
    if _db_aktif():
        log.info("Database: AKTIF (PostgreSQL) — riwayat disimpan permanen")
        init_db()
    else:
        log.info("Database: nonaktif — riwayat tidak disimpan permanen (set DATABASE_URL untuk mengaktifkan)")


@app.get("/health")
def health():
    jumlah = 0
    if qdrant.collection_exists(COLLECTION):
        jumlah = qdrant.count(collection_name=COLLECTION).count
    return {
        "status": "ok",
        "vektor": f"qdrant ({'cloud' if QDRANT_URL else 'lokal'})",
        "database": "postgresql" if _db_aktif() else "nonaktif",
        "jumlah_potongan": jumlah,
        "jumlah_dokumen": len(daftar_dokumen()),
        "cache_entries": len(_CACHE),
    }


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
    try:
        vektor = embed_banyak(potongan)
    except Exception as e:
        return {"status": "error", "pesan": f"Gagal membuat embedding: {e}"}

    doc_id = uuid.uuid4().hex[:8]
    simpan_ke_qdrant(potongan, vektor, file.filename, doc_id)
    catat_dokumen_db(file.filename, len(potongan))
    log.info("Dokumen '%s' diindeks (%d potongan, doc_id=%s)",
             file.filename, len(potongan), doc_id)

    return {
        "status": "ok",
        "doc_id": doc_id,
        "nama_file": file.filename,
        "jumlah_potongan": len(potongan),
        "pesan": "Dokumen berhasil diindeks. Silakan bertanya.",
    }


@app.get("/dokumen")
def list_dokumen():
    return {"dokumen": daftar_dokumen()}


@app.delete("/dokumen/{doc_id}")
def del_dokumen(doc_id: str):
    if not qdrant.collection_exists(COLLECTION):
        raise HTTPException(status_code=404, detail="Belum ada dokumen.")
    hapus_dokumen(doc_id)
    log.info("Dokumen doc_id=%s dihapus", doc_id)
    return {"status": "ok", "pesan": f"Dokumen {doc_id} dihapus."}


@app.get("/riwayat")
def riwayat(limit: int = 20):
    return {"database_aktif": _db_aktif(), "riwayat": ambil_riwayat(limit)}


@app.get("/statistik")
def statistik():
    if not os.path.exists(JEJAK_FILE):
        return {"total_panggilan": 0, "pesan": "Belum ada jejak."}
    baris = [json.loads(x) for x in open(JEJAK_FILE, encoding="utf-8") if x.strip()]
    if not baris:
        return {"total_panggilan": 0, "pesan": "Belum ada jejak."}
    total = len(baris)
    return {
        "total_panggilan": total,
        "cache_hit": sum(1 for b in baris if b.get("cache_hit")),
        "total_token": sum(b.get("token_total", 0) for b in baris),
        "total_biaya_usd": round(sum(b.get("biaya_usd", 0.0) for b in baris), 6),
        "rata_latency_dtk": round(sum(b.get("latency_dtk", 0.0) for b in baris) / total, 3),
        "gagal": sum(1 for b in baris if b.get("galat")),
    }


@app.post("/tanya")
def tanya(body: Pertanyaan, request: Request):
    batasi_laju(request)

    konteks = cari_konteks(body.pertanyaan)
    konteks_teks = "\n\n".join(f"[{i+1}] {c['teks']}" for i, c in enumerate(konteks))
    sumber_teks = [c["teks"] for c in konteks]
    sumber_b64 = base64.b64encode(
        json.dumps(sumber_teks, ensure_ascii=False).encode("utf-8")
    ).decode("ascii")

    prompt = (
        "Kamu adalah Cendekia, asisten riset dokumen. "
        "Jawab pertanyaan HANYA berdasarkan konteks di bawah. "
        "Jika jawabannya tidak ada di konteks, katakan dengan jujur bahwa "
        "informasi itu tidak ditemukan dalam dokumen.\n\n"
        f"Konteks:\n{konteks_teks}\n\n"
        f"Pertanyaan: {body.pertanyaan}\n"
        "Jawaban:"
    )

    kunci = _kunci("tanya", prompt)
    headers = {"X-Sumber": sumber_b64}

    # -------- 1) Cache hit: alirkan jawaban tersimpan (instan, 0 biaya) --------
    if kunci in _CACHE:
        jawaban = _CACHE[kunci]["jawaban"]
        _catat_jejak(_CACHE[kunci].get("model", "cache"), 0.0, 0, 0, cache_hit=True)
        simpan_riwayat(body.pertanyaan, jawaban)

        def stream_cache():
            for i in range(0, len(jawaban), 24):
                yield jawaban[i:i + 24]

        return StreamingResponse(
            stream_cache(), media_type="text/plain; charset=utf-8", headers=headers
        )

    # -------- 2) Panggil LLM: streaming + fallback antar-model --------
    def stream_llm():
        galat_terakhir = None
        for model in (MODEL_UTAMA, MODEL_CADANGAN):
            try:
                t0 = time.time()
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    stream=True,
                    stream_options={"include_usage": True},
                )
                acc = ""
                tok_in = tok_out = 0
                for chunk in completion:
                    if chunk.choices and chunk.choices[0].delta.content:
                        delta = chunk.choices[0].delta.content
                        acc += delta
                        yield delta
                    if getattr(chunk, "usage", None):
                        tok_in = chunk.usage.prompt_tokens or 0
                        tok_out = chunk.usage.completion_tokens or 0
                latency = round(time.time() - t0, 3)
                _CACHE[kunci] = {"model": model, "jawaban": acc}
                _simpan_cache(_CACHE)
                _catat_jejak(model, latency, tok_in, tok_out, cache_hit=False)
                simpan_riwayat(body.pertanyaan, acc)
                return
            except Exception as e:
                galat_terakhir = e
                log.warning("Model %s gagal (%s); mencoba cadangan...", model, e)
                continue
        _catat_jejak(MODEL_UTAMA, 0.0, 0, 0, cache_hit=False, galat=str(galat_terakhir))
        yield f"\n⚠️ Maaf, semua model sedang bermasalah. ({galat_terakhir})"

    return StreamingResponse(
        stream_llm(), media_type="text/plain; charset=utf-8", headers=headers
    )
