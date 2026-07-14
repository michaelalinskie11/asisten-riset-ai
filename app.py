import os
import numpy as np
import requests
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
JINA_KEY = os.getenv("JINA_API_KEY")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

st.set_page_config(page_title="Cendekia · Kecerdasan Nusantara", page_icon="✦", layout="wide")

# ================= CSS GLOBAL — tema Cendekia (bukan f-string!) =================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400..600&family=Inter:wght@400;500;600&family=Space+Mono:wght@400;700&display=swap');

.stApp { background: #0a0a0b; }

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #b8b6b0; }
h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #ece9e2 !important; font-weight: 500 !important; letter-spacing: .2px; }

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* Pesan chat */
.stChatMessage {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(236,233,226,0.10);
    border-radius: 14px;
    animation: fadeInUp 0.5s ease;
}
@keyframes fadeInUp { from {opacity:0; transform:translateY(12px);} to {opacity:1; transform:translateY(0);} }

/* Kotak input chat */
[data-testid="stChatInput"] {
    border: 1px solid rgba(236,233,226,0.12);
    border-radius: 14px;
    background: #111113;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(217,164,65,0.6);
    box-shadow: 0 0 20px rgba(217,164,65,0.12);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111113;
    border-right: 1px solid rgba(236,233,226,0.08);
}

/* Tombol emas */
.stButton button {
    border: 1px solid rgba(217,164,65,0.5);
    border-radius: 11px;
    color: #0a0a0b;
    background: #d9a441;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton button:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(217,164,65,0.25);
}

/* Expander sumber & file uploader */
[data-testid="stExpander"] { border: 1px solid rgba(236,233,226,0.08); border-radius: 12px; }
[data-testid="stFileUploader"] section { border: 1px dashed rgba(236,233,226,0.15); background: transparent; }
.stAlert { border-radius: 12px; }

::-webkit-scrollbar { width: 9px; }
::-webkit-scrollbar-thumb { background: #d9a441; border-radius: 5px; }
</style>""", unsafe_allow_html=True)

# ================= HERO — gaya Cendekia (obsidian + emas + Fraunces) =================
HERO = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..500&family=Inter:wght@400;500&family=Space+Mono:wght@400;700&display=swap');
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:#0a0a0b; height:280px; position:relative; overflow:hidden; }
.glow { position:absolute; width:620px; height:420px; top:-170px; right:-80px; border-radius:50%;
    background:radial-gradient(circle, rgba(217,164,65,0.10), transparent 60%); }
.wrap { position:relative; z-index:2; height:100%; display:flex; flex-direction:column; justify-content:center; padding-left:10px; }
.label { font-family:'Space Mono',monospace; font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#d9a441; margin-bottom:18px; }
.label .dot { opacity:.5; }
h1 { font-family:'Fraunces',serif; font-size:52px; line-height:1.02; color:#ece9e2; font-weight:400; letter-spacing:.3px; }
.type { color:transparent; background:linear-gradient(90deg,#f8dd95,#e0ad4c,#9c6f1f); -webkit-background-clip:text; background-clip:text; font-style:italic; }
.cursor { display:inline-block; width:2px; height:40px; background:#d9a441; margin-left:5px; vertical-align:-7px; animation:blink 0.9s steps(1) infinite; }
@keyframes blink { 50% { opacity:0; } }
.sub { margin-top:18px; color:#b8b6b0; font-size:15px; max-width:560px; line-height:1.6; }
</style></head>
<body>
<div class="glow"></div>
<div class="wrap">
  <div class="label">✦ CENDEKIA <span class="dot">·</span> KECERDASAN NUSANTARA</div>
  <h1>Dari dokumen, menjadi <span class="type" id="tw"></span><span class="cursor"></span></h1>
  <p class="sub">Kecerdasan yang tenang, jawaban yang bercahaya. Unggah dokumenmu, lalu tanyakan apa saja — dijawab lengkap dengan sumbernya.</p>
</div>
<script>
const phrases = ["kejelasan.","jawaban.","wawasan.","ringkasan.","kepastian."];
let i=0, j=0, del=false;
const el=document.getElementById('tw');
function tick(){
  const p=phrases[i];
  el.textContent=p.substring(0,j);
  if(!del){ j++; if(j>p.length){ del=true; setTimeout(tick,1600); return; } }
  else { j--; if(j<0){ del=false; i=(i+1)%phrases.length; j=0; } }
  setTimeout(tick, del?40:90);
}
tick();
</script>
</body></html>"""
components.html(HERO, height=280, scrolling=False)

# ================= Fungsi bantu =================
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

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= SIDEBAR =================
with st.sidebar:
    st.title("✦ Cendekia")
    st.caption("Asisten riset dokumen ber-AI.")
    st.divider()
    file = st.file_uploader("Unggah dokumen PDF", type="pdf")
    if file and st.session_state.get("nama_file") != file.name:
        with st.spinner("Memproses dokumen..."):
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
            st.session_state.messages = []
        st.success(f"'{file.name}' siap ({len(chunks)} bagian)")
    if st.session_state.get("nama_file"):
        st.info(f"Dokumen aktif:\n\n**{st.session_state.nama_file}**")
        if st.button("Bersihkan percakapan"):
            st.session_state.messages = []
            st.rerun()
    st.divider()
    st.caption("Dibuat oleh Michael Alinskie · Groq + Jina AI")

# ================= CHAT =================
if not st.session_state.get("nama_file"):
    st.info("Mulai dengan mengunggah file PDF di panel kiri.")
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sumber"):
            with st.expander("Lihat sumber"):
                for nilai, teks in msg["sumber"]:
                    st.markdown(f"**Kemiripan {nilai:.2f}**")
                    st.caption(teks)

if pertanyaan := st.chat_input("Tanya sesuatu tentang dokumenmu..."):
    st.session_state.messages.append({"role": "user", "content": pertanyaan})
    with st.chat_message("user"):
        st.markdown(pertanyaan)
    with st.chat_message("assistant"):
        with st.spinner("Mencari bagian relevan..."):
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

Pertanyaan: {pertanyaan}"""
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        def alir():
            for bagian in stream:
                isi = bagian.choices[0].delta.content
                if isi:
                    yield isi
        jawaban = st.write_stream(alir())
        sumber = [(nilai, st.session_state.chunks[i]) for nilai, i in top]
        with st.expander("Lihat sumber"):
            for nilai, teks in sumber:
                st.markdown(f"**Kemiripan {nilai:.2f}**")
                st.caption(teks)
    st.session_state.messages.append({
        "role": "assistant",
        "content": jawaban,
        "sumber": sumber,
    })
