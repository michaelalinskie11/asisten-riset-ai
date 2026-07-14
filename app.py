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
hr { border-color: rgba(236,233,226,0.08) !important; }

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111113, #0c0c0e);
    border-right: 1px solid rgba(236,233,226,0.08);
}
[data-testid="stSidebar"] .block-container { padding-top: 26px; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stSidebar"] p { color: #7d7d84; }

.brand { display:flex; align-items:center; gap:13px; margin-bottom:6px; }
.brand .mark {
    width:44px; height:44px; border-radius:13px; display:grid; place-items:center;
    font-size:21px; color:#0a0a0b; background:linear-gradient(135deg,#f8dd95,#d9a441);
    box-shadow:0 6px 18px rgba(217,164,65,.32);
}
.brand .bname { font-family:'Fraunces',serif; font-size:23px; color:#ece9e2; line-height:1; }
.brand .btag { font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2.5px; color:#d9a441; margin-top:5px; }

.sec-label { font-family:'Space Mono',monospace; font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#7d7d84; margin:6px 0 10px; }

.doc-chip { display:flex; align-items:center; gap:12px; padding:13px 14px; border-radius:14px;
    background:#131315; border:1px solid rgba(217,164,65,0.22); }
.doc-chip .doc-ic { width:34px; height:34px; border-radius:9px; display:grid; place-items:center; font-size:16px;
    background:rgba(217,164,65,0.10); border:1px solid rgba(217,164,65,0.3); }
.doc-chip .doc-l { font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2px; text-transform:uppercase; color:#7d7d84; }
.doc-chip .doc-n { font-family:'Fraunces',serif; font-size:15px; color:#ece9e2; margin-top:2px; word-break:break-word; }

/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section {
    background: #131315;
    border: 1.5px dashed rgba(217,164,65,0.40);
    border-radius: 16px;
    padding: 20px 16px;
    transition: all .25s ease;
}
[data-testid="stFileUploaderDropzone"]:hover, [data-testid="stFileUploader"] section:hover {
    border-color: rgba(217,164,65,0.85);
    background: #17171a;
    box-shadow: 0 0 26px rgba(217,164,65,0.12);
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: #b8b6b0; }
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small { color: #7d7d84 !important; }
[data-testid="stFileUploaderDropzone"] svg { fill:#d9a441 !important; color:#d9a441 !important; }
[data-testid="stFileUploader"] button {
    color:#d9a441 !important; background:rgba(217,164,65,0.08) !important;
    border:1px solid rgba(217,164,65,0.5) !important; border-radius:10px !important; font-weight:600 !important;
}
[data-testid="stFileUploader"] button:hover { background:rgba(217,164,65,0.16) !important; box-shadow:none !important; transform:none !important; }

/* ---------- TOMBOL EMAS (umum) ---------- */
.stButton button {
    border: 1px solid rgba(217,164,65,0.5); border-radius: 11px;
    color: #0a0a0b; background: #d9a441; font-weight: 600; transition: all 0.2s ease;
}
.stButton button:hover { filter: brightness(1.08); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(217,164,65,0.25); }

/* ---------- CHAT ---------- */
.stChatMessage {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(236,233,226,0.10);
    border-radius: 14px;
    animation: fadeInUp 0.5s ease;
}
@keyframes fadeInUp { from {opacity:0; transform:translateY(12px);} to {opacity:1; transform:translateY(0);} }
[data-testid="stChatInput"] { border: 1px solid rgba(236,233,226,0.12); border-radius: 14px; background: #111113; }
[data-testid="stChatInput"]:focus-within { border-color: rgba(217,164,65,0.6); box-shadow: 0 0 20px rgba(217,164,65,0.12); }

/* ---------- EXPANDER & ALERT ---------- */
[data-testid="stExpander"] { border: 1px solid rgba(236,233,226,0.08); border-radius: 12px; background:#0e0e10; }
[data-testid="stAlert"] { background:#131315; border:1px solid rgba(236,233,226,0.10); border-left:3px solid #d9a441; border-radius:12px; color:#b8b6b0; }

::-webkit-scrollbar { width: 9px; }
::-webkit-scrollbar-thumb { background: #d9a441; border-radius: 5px; }

/* ---------- EMPTY STATE ---------- */
.empty { max-width:560px; margin:26px auto 0; text-align:center; padding:44px 34px;
    border:1px solid rgba(236,233,226,0.09); border-radius:22px;
    background:radial-gradient(600px 260px at 50% -10%, rgba(217,164,65,0.07), transparent 60%), #0d0d0f; }
.empty .em-mark { width:58px; height:58px; margin:0 auto 20px; border-radius:16px; display:grid; place-items:center;
    font-size:27px; color:#0a0a0b; background:linear-gradient(135deg,#f8dd95,#d9a441); box-shadow:0 8px 26px rgba(217,164,65,.3); }
.empty .em-title { font-family:'Fraunces',serif; font-size:27px; color:#ece9e2; margin-bottom:12px; }
.empty .em-sub { font-family:'Inter',sans-serif; font-size:14.5px; color:#b8b6b0; line-height:1.65; }
.empty .em-hint { font-family:'Space Mono',monospace; font-size:11px; letter-spacing:2px; color:#d9a441; margin-top:22px; text-transform:uppercase; }
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
    st.markdown("""<div class="brand">
      <div class="mark">✦</div>
      <div><div class="bname">Cendekia</div><div class="btag">KECERDASAN NUSANTARA</div></div>
    </div>""", unsafe_allow_html=True)
    st.caption("Asisten riset dokumen ber-AI — membaca, memahami, menjawab dengan sumber.")
    st.divider()
    st.markdown('<div class="sec-label">Dokumen</div>', unsafe_allow_html=True)
    file = st.file_uploader("Unggah dokumen PDF", type="pdf", label_visibility="collapsed")
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
            st.session_state.jumlah = len(chunks)
            st.session_state.messages = []
        st.success(f"'{file.name}' siap — {len(chunks)} bagian.")
    if st.session_state.get("nama_file"):
        st.markdown(
            f'<div class="doc-chip"><div class="doc-ic">📄</div>'
            f'<div><div class="doc-l">Dokumen aktif · {st.session_state.get("jumlah", 0)} bagian</div>'
            f'<div class="doc-n">{st.session_state.nama_file}</div></div></div>',
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("🗑️  Bersihkan percakapan", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    st.divider()
    st.caption("Dibuat oleh Michael Alinskie · Groq + Jina AI")

# ================= CHAT =================
if not st.session_state.get("nama_file"):
    st.markdown("""<div class="empty">
      <div class="em-mark">✦</div>
      <div class="em-title">Selamat datang di Cendekia</div>
      <div class="em-sub">Unggah sebuah dokumen PDF pada panel di sebelah kiri untuk memulai. Cendekia akan membaca dokumenmu, memahami maknanya, lalu menjawab pertanyaanmu — lengkap dengan sumber yang bisa kamu percaya.</div>
      <div class="em-hint">← Mulai dari panel kiri</div>
    </div>""", unsafe_allow_html=True)
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
