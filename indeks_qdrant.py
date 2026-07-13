# =====================================================
#  indeks_qdrant.py — isi data awal ke Qdrant
#  Otomatis pilih Cloud (kalau QDRANT_URL di-set di .env)
#  atau lokal. Baca embeddings.json lalu simpan.
#
#  Jalankan sekali:  python indeks_qdrant.py
# =====================================================
import os
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = "cendekia"

# --- 1. Muat cache ---
with open("embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)
chunks = data["chunks"]
vectors = data["vectors"]
dim = len(vectors[0])
print(f"Membaca {len(chunks)} potongan, dimensi vektor = {dim}")

# --- 2. Sambung ke Qdrant (cloud atau lokal) ---
if QDRANT_URL:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("Menyimpan ke Qdrant CLOUD…")
else:
    client = QdrantClient(path="./qdrant_data")
    print("Menyimpan ke Qdrant LOKAL…")

# --- 3. Buat koleksi bersih ---
if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
)

# --- 4. Simpan semua potongan ---
points = [
    PointStruct(id=i, vector=vectors[i], payload={"teks": chunks[i]})
    for i in range(len(chunks))
]
client.upsert(collection_name=COLLECTION, points=points)

jumlah = client.count(collection_name=COLLECTION).count
print(f"Selesai! {jumlah} potongan tersimpan di Qdrant. \u2705")
client.close()   # tutup rapi (hindari pesan error saat keluar di Windows)
