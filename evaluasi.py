"""
Evaluasi RAG — Cendekia
=======================
Mengukur kualitas sistem RAG secara otomatis dengan 4 metrik:

  1. Retrieval Hit Rate  — apakah potongan dokumen yang relevan berhasil diambil?
  2. Answer Accuracy      — apakah jawaban memuat fakta yang benar?
  3. Faithfulness (juri)  — apakah jawaban HANYA berdasar konteks (tidak mengarang)?
  4. Relevance (juri)     — apakah jawaban benar-benar menjawab pertanyaan?

Metrik 3 & 4 dinilai oleh 'LLM-as-judge' (model LLM lain berperan sebagai juri).

Cara pakai:
    .\\venv\\Scripts\\Activate.ps1
    python evaluasi.py

Butuh: GROQ_API_KEY & JINA_API_KEY di .env, serta dokumen.txt atau dokumen.pdf.
"""
import os
import re
import json
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

GEN_MODEL = "llama-3.1-8b-instant"        # model yang menjawab (sama seperti aplikasi)
JUDGE_MODEL = "llama-3.3-70b-versatile"   # model juri (lebih pintar); fallback ke GEN_MODEL
TOP_K = 5

# ================= DATASET UJI =================
# 'kunci' = kata/frasa yang HARUS muncul untuk dianggap benar.
# tipe 'fakta'   -> jawaban harus memuat fakta.
# tipe 'di_luar' -> pertanyaan di luar dokumen; sistem HARUS menolak menjawab.
DATASET = [
    {"tanya": "Kapan dan di mana NusantaraByte didirikan?", "kunci": ["2023", "Surabaya"], "tipe": "fakta"},
    {"tanya": "Siapa CEO NusantaraByte?", "kunci": ["Michael Alinskie"], "tipe": "fakta"},
    {"tanya": "Apa nama produk utama NusantaraByte?", "kunci": ["Lontara"], "tipe": "fakta"},
    {"tanya": "Berapa harga paket Profesional?", "kunci": ["450"], "tipe": "fakta"},
    {"tanya": "Fitur bahasa daerah apa yang direncanakan pada Q4 2026?", "kunci": ["Jawa", "Bali"], "tipe": "fakta"},
    {"tanya": "Berapa target pengguna aktif bulanan (MAU) di akhir 2026?", "kunci": ["30"], "tipe": "fakta"},
    {"tanya": "Siapa pelatih tim nasional sepak bola Argentina?", "kunci": [], "tipe": "di_luar"},
]

# ================= Fungsi inti RAG =================
def baca_dokumen():
    # Utamakan dokumen.pdf — basis pengetahuan LENGKAP (berisi semua fakta uji).
    if os.path.exists("dokumen.pdf"):
        from pypdf import PdfReader
        reader = PdfReader("dokumen.pdf")
        teks = ""
        for hal in reader.pages:
            t = hal.extract_text()
            if t:
                teks += t + "\n"
        print("   Sumber: dokumen.pdf")
        return teks
    if os.path.exists("dokumen.txt"):
        with open("dokumen.txt", encoding="utf-8") as f:
            print("   Sumber: dokumen.txt")
            return f.read()
    raise FileNotFoundError("Tidak menemukan dokumen.pdf atau dokumen.txt di folder ini.")

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

def ambil_konteks(q_vec, chunks, vectors, k=TOP_K):
    skor = sorted(
        [(kemiripan(q_vec, v), i) for i, v in enumerate(vectors)],
        reverse=True,
    )
    top = skor[:k]
    return "\n---\n".join(chunks[i] for _, i in top)

def jawab(pertanyaan, konteks):
    prompt = f"""Kamu asisten yang menjawab berdasarkan KONTEKS dokumen di bawah.
Baca SELURUH konteks dengan teliti sebelum menyimpulkan.
- Jika informasinya ada (walau tersebar di beberapa bagian), rangkum dan jawab dengan jelas.
- Hanya jika benar-benar tidak ada di konteks, katakan "Tidak ada di dokumen."

KONTEKS:
{konteks}

Pertanyaan: {pertanyaan}"""
    resp = client.chat.completions.create(
        model=GEN_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

# ================= LLM-as-judge =================
def ambil_json(teks):
    teks = teks.replace("```json", "").replace("```", "")
    m = re.search(r"\{.*\}", teks, re.S)
    return json.loads(m.group(0)) if m else None

def juri(pertanyaan, konteks, jawaban):
    contoh = '{"faithfulness": 5, "relevance": 5}'
    prompt = f"""Kamu adalah juri evaluasi sistem RAG yang ketat dan objektif.
Nilai JAWABAN terhadap KONTEKS dan PERTANYAAN dengan dua skor:
- faithfulness (1-5): seberapa jawaban HANYA didasarkan pada KONTEKS. 5 = sepenuhnya berdasar konteks & tidak mengarang; 1 = banyak mengarang.
- relevance (1-5): seberapa jawaban menjawab PERTANYAAN. 5 = sangat relevan; 1 = tidak nyambung.
Jika jawaban dengan benar menyatakan informasi tidak ada di dokumen (padahal memang tidak ada), beri faithfulness 5.

Balas HANYA JSON valid tanpa teks lain, contoh format: {contoh}

KONTEKS:
{konteks}

PERTANYAAN: {pertanyaan}
JAWABAN: {jawaban}"""
    for model in (JUDGE_MODEL, GEN_MODEL):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            data = ambil_json(resp.choices[0].message.content)
            if data:
                return int(data["faithfulness"]), int(data["relevance"])
        except Exception:
            continue
    return 0, 0

# ================= Jalankan evaluasi =================
def mengandung(teks, kunci):
    t = teks.lower()
    return any(k.lower() in t for k in kunci)

def main():
    if not JINA_KEY or not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY / JINA_API_KEY belum ada di .env")
        return

    print("📚 Menyiapkan basis pengetahuan...")
    teks = baca_dokumen()
    chunks = potong(teks)
    vectors = embed(chunks)
    print(f"   {len(chunks)} potongan, dimensi vektor = {len(vectors[0])}\n")

    baris = []
    hit_retrieval, benar_jawaban, tolak_benar = 0, 0, 0
    n_fakta, n_diluar = 0, 0
    total_faith, total_rel = 0, 0

    for kasus in DATASET:
        q = kasus["tanya"]
        q_vec = embed([q])[0]
        konteks = ambil_konteks(q_vec, chunks, vectors)
        jwb = jawab(q, konteks)
        faith, rel = juri(q, konteks, jwb)
        total_faith += faith
        total_rel += rel

        if kasus["tipe"] == "fakta":
            n_fakta += 1
            r_hit = mengandung(konteks, kasus["kunci"])
            a_hit = mengandung(jwb, kasus["kunci"])
            hit_retrieval += int(r_hit)
            benar_jawaban += int(a_hit)
            status = "✅" if a_hit else "❌"
            retr = "✓" if r_hit else "✗"
        else:
            n_diluar += 1
            menolak = mengandung(jwb, ["tidak ada", "tidak disebut", "tidak terdapat"])
            tolak_benar += int(menolak)
            status = "✅" if menolak else "❌ (halusinasi!)"
            retr = "-"

        baris.append((q, jwb.replace("\n", " "), retr, faith, rel, status))
        print(f"• {q}\n  → {jwb}\n  retrieval={retr}  faith={faith}/5  rel={rel}/5  {status}\n")

    n = len(DATASET)
    rr = hit_retrieval / n_fakta * 100 if n_fakta else 0
    aa = benar_jawaban / n_fakta * 100 if n_fakta else 0
    tr = tolak_benar / n_diluar * 100 if n_diluar else 0
    af = total_faith / n
    ar = total_rel / n

    print("=" * 56)
    print("  📊 SKOR EVALUASI RAG — CENDEKIA")
    print("=" * 56)
    print(f"  Retrieval Hit Rate               : {rr:5.1f}%  ({hit_retrieval}/{n_fakta})")
    print(f"  Answer Accuracy                  : {aa:5.1f}%  ({benar_jawaban}/{n_fakta})")
    print(f"  Penolakan benar (anti-halusinasi): {tr:5.1f}%  ({tolak_benar}/{n_diluar})")
    print(f"  Rata-rata Faithfulness           : {af:4.2f}/5")
    print(f"  Rata-rata Relevance              : {ar:4.2f}/5")
    print("=" * 56)

    # Tulis laporan markdown untuk portofolio
    with open("LAPORAN_EVALUASI.md", "w", encoding="utf-8") as f:
        f.write("# Laporan Evaluasi RAG — Cendekia\n\n")
        f.write("Evaluasi otomatis atas sistem Retrieval-Augmented Generation.\n\n")
        f.write("## Ringkasan Skor\n\n")
        f.write("| Metrik | Skor |\n|---|---|\n")
        f.write(f"| Retrieval Hit Rate | {rr:.1f}% ({hit_retrieval}/{n_fakta}) |\n")
        f.write(f"| Answer Accuracy | {aa:.1f}% ({benar_jawaban}/{n_fakta}) |\n")
        f.write(f"| Penolakan benar (anti-halusinasi) | {tr:.1f}% ({tolak_benar}/{n_diluar}) |\n")
        f.write(f"| Rata-rata Faithfulness | {af:.2f}/5 |\n")
        f.write(f"| Rata-rata Relevance | {ar:.2f}/5 |\n\n")
        f.write("## Rincian per Pertanyaan\n\n")
        f.write("| Pertanyaan | Jawaban | Retrieval | Faith | Rel | Status |\n")
        f.write("|---|---|:--:|:--:|:--:|:--:|\n")
        for q, jwb, retr, faith, rel, status in baris:
            jwb_pendek = (jwb[:90] + "...") if len(jwb) > 90 else jwb
            f.write(f"| {q} | {jwb_pendek} | {retr} | {faith} | {rel} | {status} |\n")
        f.write(f"\n*Faithfulness & Relevance dinilai oleh LLM-as-judge ({JUDGE_MODEL}).*\n")
    print("\n📝 Laporan lengkap tersimpan di 'LAPORAN_EVALUASI.md'")

if __name__ == "__main__":
    main()
