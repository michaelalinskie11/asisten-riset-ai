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

st.set_page_config(page_title="Cendekia AI", page_icon="✦", layout="wide")

# ================= CSS GLOBAL (bukan f-string!) =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&display=swap');

.stApp {
    background:
        radial-gradient(1000px 500px at 15% -10%, rgba(124,92,255,0.18), transparent),
        radial-gradient(900px 500px at 90% 0%, rgba(0,229,255,0.12), transparent),
        linear-gradient(180deg, #070a1a, #05070f);
    background-attachment: fixed;
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

.stChatMessage, .stButton button, [data-testid="stChatInput"] {
    transition: all 0.3s cubic-bezier(.2,.7,.3,1);
}
.stChatMessage {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(124,92,255,0.22);
    border-radius: 18px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    animation: fadeInUp 0.5s ease;
}
.stChatMessage:hover {
    border-color: rgba(0,229,255,0.4);
    box-shadow: 0 0 26px rgba(0,229,255,0.10);
}
@keyframes fadeInUp { from {opacity:0; transform:translateY(14px);} to {opacity:1; transform:translateY(0);} }

[data-testid="stChatInput"] {
    border: 1px solid rgba(124,92,255,0.35);
    border-radius: 16px;
    box-shadow: 0 0 24px rgba(124,92,255,0.12);
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(255,207,92,0.6);
    box-shadow: 0 0 26px rgba(255,207,92,0.18);
}
[data-testid="stSidebar"] {
    background: rgba(7,10,26,0.75);
    border-right: 1px solid rgba(124,92,255,0.15);
    backdrop-filter: blur(14px);
}
.stButton button {
    border: 1px solid rgba(255,207,92,0.45);
    border-radius: 12px;
    color: #ffe9b0;
    background: rgba(255,207,92,0.06);
    font-weight: 600;
}
.stButton button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 18px rgba(255,207,92,0.4);
    border-color: rgba(255,207,92,0.8);
}
[data-testid="stHeader"] { background: transparent; }
::-webkit-scrollbar { width: 9px; }
::-webkit-scrollbar-thumb { background: linear-gradient(#7c5cff, #00e5ff); border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ================= HERO (aurora + judul + typing looping) =================
HERO = """
<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&display=swap');
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:#070a1a; overflow:hidden; height:300px; position:relative; }
.orb { position:absolute; border-radius:50%; filter:blur(70px); opacity:0.55; animation:float 14s ease-in-out infinite; }
.orb1 { width:260px; height:260px; background:#7c5cff; top:-60px; left:8%; }
.orb2 { width:220px; height:220px; background:#00e5ff; bottom:-70px; left:38%; animation-delay:-4s; }
.orb3 { width:200px; height:200px; background:#ffcf5c; top:-40px; right:10%; animation-delay:-8s; }
@keyframes float { 0%,100%{transform:translate(0,0);} 50%{transform:translate(20px,30px);} }
.wrap { position:relative; z-index:2; height:100%; display:flex; flex-direction:column; justify-content:center; padding-left:44px; }
.badge { width:fit-content; font-size:12px; letter-spacing:2px; text-transform:uppercase; color:#ffcf5c;
    border:1px solid rgba(255,207,92,0.4); padding:5px 14px; border-radius:20px; margin-bottom:16px; background:rgba(255,207,92,0.06); }
h1 { font-family:'Space Grotesk',sans-serif; font-size:46px; line-height:1.05; color:#eef1ff; font-weight:700; }
.grad { background:linear-gradient(90deg,#7c5cff,#00e5ff,#ffcf5c); background-size:200% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; animation:shine 5s linear infinite; }
@keyframes shine { to { background-position:200% center; } }
.type { color:#ffcf5c; font-family:'Space Grotesk',sans-serif; font-weight:700; }
.cursor { display:inline-block; width:3px; height:34px; background:#ffcf5c; margin-left:4px; vertical-align:-6px;
    box-shadow:0 0 10px #ffcf5c; animation:blink 0.9s steps(1) infinite; }
@keyframes blink { 50% { opacity:0; } }
.sub { margin-top:14px; color:#9aa3c7; font-size:15px; max-width:540px; }
</style></head><body>
<div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div>
<div class="wrap">
  <span class="badge">✦ Cendekia AI</span>
  <h1><span class="grad">Ubah dokumenmu</span><br><span class="type" id="tw"></span><span class="cursor"></span></h1>
  <p class="sub">Unggah dokumen apa pun, tanya dengan bahasa natural, dan dapatkan jawaban akurat lengkap dengan sumbernya.</p>
</div>
<script>
const phrases = ["jadi jawaban.","jadi wawasan.","dalam sekejap.","dengan sumber tepercaya."];
let i=0, j=0, del=false;
const el=document.getElementById('tw');
function tick(){
  const p=phrases[i];
  el.textContent=p.substring(0,j);
  if(!del){ j++; if(j>p.length){ del=true; setTimeout(tick,1500); return; } }
  else { j--; if(j<0){ del=false; i=(i+1)%phrases.length; j=0; } }
  setTimeout(tick, del?40:85);
}
tick();
</script></body></html>
"""
components.html(HERO, height=300, scrolling=False)

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

    file = st.file_uploader("📎 Unggah dokumen PDF", type="pdf")

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
        st.success(f"✅ '{file.name}' siap ({len(chunks)} bagian)")

    if st.session_state.get("nama_file"):
        st.info(f"📄 Dokumen aktif:\n\n**{st.session_state.nama_file}**")
        if st.button("🗑️ Bersihkan percakapan"):
            st.session_state.messages = []
            st.rerun()

    st.divider()
    st.caption("Dibuat oleh Michael Alinskie · Groq + Jina AI")

# ================= CHAT =================
if not st.session_state.get("nama_file"):
    st.info("👈 Mulai dengan mengunggah file PDF di panel kiri.")
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sumber"):
            with st.expander("📌 Lihat sumber"):
                for nilai, teks in msg["sumber"]:
                    st.markdown(f"**Kemiripan {nilai:.2f}**")
                    st.caption(teks)

if pertanyaan := st.chat_input("Tanya sesuatu tentang dokumenmu..."):
    st.session_state.messages.append({"role": "user", "content": pertanyaan})
    with st.chat_message("user"):
        st.markdown(pertanyaan)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Mencari bagian relevan..."):
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
        with st.expander("📌 Lihat sumber"):
            for nilai, teks in sumber:
                st.markdown(f"**Kemiripan {nilai:.2f}**")
                st.caption(teks)

    st.session_state.messages.append({
        "role": "assistant",
        "content": jawaban,
        "sumber": sumber,
    })