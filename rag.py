import os
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

# 1. BACA dokumen dari file PDF
reader = PdfReader("dokumen.pdf")
isi_dokumen = ""
for halaman in reader.pages:
    teks = halaman.extract_text()
    if teks:  # kadang ada halaman kosong / gambar
        isi_dokumen += teks + "\n"

print("PDF terbaca:", len(reader.pages), "halaman,", len(isi_dokumen), "karakter\n")

# 2. Ambil pertanyaan dari kamu
pertanyaan = input("Tanya tentang dokumen: ")

# 3. Gabungkan dokumen + pertanyaan jadi prompt (inti RAG)
prompt = f"""Jawab pertanyaan HANYA berdasarkan dokumen di bawah ini.
Jika jawabannya tidak ada di dokumen, katakan "Tidak ada di dokumen."

=== DOKUMEN ===
{isi_dokumen}
=== AKHIR DOKUMEN ===

Pertanyaan: {pertanyaan}
"""

# 4. Kirim ke AI
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
)

print("\nJawaban AI:\n")
print(response.choices[0].message.content)