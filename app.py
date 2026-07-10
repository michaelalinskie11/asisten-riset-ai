import os
import numpy as np
import requests
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
JINA_KEY = os.getenv("JINA_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

# ---------- fungsi bantu (sama seperti sebelumnya) ----------
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

def kemiripan(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ---------- tampilan web ----------
st.title("📚 Asisten Riset Dokumen AI")
st.caption("Upload sebuah PDF, lalu tanya apa saja tentang isinya.")

file = st.file_uploader("Pilih file PDF", type="pdf")

if file:
    # proses dokumen hanya sekali per file (disimpan di session_state)
    if st.session_state.get("nama_file") != file.name:
        with st.spinner("Membaca & memproses dokumen..."):
            reader = PdfReader(file)
            teks = ""
            for hal in reader.pages:
                t = hal.extract_text()
                if t:
                    teks += t + "\n"
            chunks = potong(teks)
            st.session_state.chunks = chunks
            st.session_state.vectors = embed(chunks)
            st.session_state.nama_file = file.name
        st.success(f"Dokumen '{file.name}' siap! ({len(st.session_state.chunks)} bagian)")

    pertanyaan = st.text_input("Tanya sesuatu tentang dokumen:")

    if pertanyaan:
        with st.spinner("Mencari jawaban..."):
            q_vec = embed([pertanyaan])[0]
            skor = sorted(
                [(kemiripan(q_vec, v), i) for i, v in enumerate(st.session_state.vectors)],
                reverse=True,
            )
            top = skor[:3]
            konteks = "\n---\n".join(st.session_state.chunks[i] for _, i in top)

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
            jawaban = resp.choices[0].message.content

        st.markdown("### 💬 Jawaban")
        st.write(jawaban)

        with st.expander("📌 Lihat sumber yang digunakan"):
            for nilai, i in top:
                st.markdown(f"**Bagian {i}** — kemiripan {nilai:.2f}")
                st.caption(st.session_state.chunks[i])