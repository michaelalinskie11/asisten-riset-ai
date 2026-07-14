import os
import ast
import json
import operator
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

/* ---------- LATAR + ANIMASI GLOBAL ---------- */
.stApp { background: #0a0a0b; }
.stApp::before {
    content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:
        radial-gradient(680px 380px at 12% 6%, rgba(217,164,65,0.065), transparent 60%),
        radial-gradient(560px 360px at 88% 94%, rgba(217,164,65,0.045), transparent 60%);
    animation: drift 20s ease-in-out infinite alternate;
}
@keyframes drift { from { transform: translate3d(0,-12px,0); } to { transform: translate3d(0,12px,0); } }
[data-testid="stAppViewContainer"], [data-testid="stMain"], section.main { position:relative; z-index:1; }

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #b8b6b0; }
h1, h2, h3 { font-family: 'Fraunces', serif !important; color: #ece9e2 !important; font-weight: 500 !important; letter-spacing: .2px; }

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
hr { border-color: rgba(236,233,226,0.08) !important; }

[data-testid="stMain"] .block-container { max-width: 900px; padding-top: 10px; animation: fadeUp .6s ease both; }

@keyframes fadeUp { from {opacity:0; transform:translateY(16px);} to {opacity:1; transform:translateY(0);} }
@keyframes floaty { 0%,100% {transform:translateY(0);} 50% {transform:translateY(-4px);} }
@keyframes glowpulse { 0%,100% {box-shadow:0 0 0 rgba(217,164,65,0);} 50% {box-shadow:0 0 24px rgba(217,164,65,0.11);} }

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111113, #0b0b0d);
    border-right: 1px solid rgba(236,233,226,0.08);
}
[data-testid="stSidebar"] .block-container { padding-top: 26px; animation: fadeUp .7s ease both; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"], [data-testid="stSidebar"] p { color: #7d7d84; }

.brand { display:flex; align-items:center; gap:13px; margin-bottom:6px; }
.brand .mark {
    width:44px; height:44px; border-radius:13px; display:grid; place-items:center;
    font-size:21px; color:#0a0a0b; background:linear-gradient(135deg,#f8dd95,#d9a441);
    box-shadow:0 6px 18px rgba(217,164,65,.32); animation: floaty 4.5s ease-in-out infinite;
}
.brand .bname { font-family:'Fraunces',serif; font-size:23px; color:#ece9e2; line-height:1; }
.brand .btag { font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2.5px; color:#d9a441; margin-top:5px; }

.sec-label { font-family:'Space Mono',monospace; font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#7d7d84; margin:6px 0 10px; }

.doc-chip { display:flex; align-items:center; gap:12px; padding:13px 14px; border-radius:14px;
    background:#131315; border:1px solid rgba(217,164,65,0.22); animation: fadeUp .5s ease both; }
.doc-chip .doc-ic { width:34px; height:34px; border-radius:9px; display:grid; place-items:center; font-size:16px;
    background:rgba(217,164,65,0.10); border:1px solid rgba(217,164,65,0.3); }
.doc-chip .doc-l { font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2px; text-transform:uppercase; color:#7d7d84; }
.doc-chip .doc-n { font-family:'Fraunces',serif; font-size:15px; color:#ece9e2; margin-top:2px; word-break:break-word; }

/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section {
    background: #131315; border: 1.5px dashed rgba(217,164,65,0.40); border-radius: 16px;
    padding: 26px 18px; transition: all .25s ease; animation: glowpulse 4s ease-in-out infinite;
}
[data-testid="stFileUploaderDropzone"]:hover, [data-testid="stFileUploader"] section:hover {
    border-color: rgba(217,164,65,0.9); background: #17171a; transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0,0,0,.35), 0 0 26px rgba(217,164,65,0.14); animation: none;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: #b8b6b0; }
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small { color: #7d7d84 !important; }
[data-testid="stFileUploaderDropzone"] svg { fill:#d9a441 !important; color:#d9a441 !important; }
[data-testid="stFileUploader"] button {
    color:#d9a441 !important; background:rgba(217,164,65,0.08) !important;
    border:1px solid rgba(217,164,65,0.5) !important; border-radius:10px !important; font-weight:600 !important;
    transition: all .2s ease !important;
}
[data-testid="stFileUploader"] button:hover { background:rgba(217,164,65,0.18) !important; transform:none !important; }

/* ---------- TOMBOL EMAS (umum) ---------- */
.stButton button {
    position:relative; overflow:hidden; border: 1px solid rgba(217,164,65,0.5); border-radius: 11px;
    color: #0a0a0b; background: linear-gradient(135deg,#f2cf7d,#d9a441); font-weight: 600; transition: all 0.22s ease;
}
.stButton button:hover { filter: brightness(1.06); transform: translateY(-1px); box-shadow: 0 8px 22px rgba(217,164,65,0.30); }
.stButton button:active { transform: translateY(0) scale(.99); }

/* ---------- CHAT ---------- */
.stChatMessage {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(236,233,226,0.10);
    border-radius: 16px; animation: fadeUp 0.5s ease both; transition: border-color .25s ease, box-shadow .25s ease;
}
.stChatMessage:hover { border-color: rgba(217,164,65,0.28); box-shadow: 0 8px 26px rgba(0,0,0,0.25); }
.stChatMessage img, .stChatMessage [data-testid*="Avatar"] { box-shadow: 0 0 0 1px rgba(217,164,65,0.4); border-radius:50%; }
[data-testid="stChatInput"] { border: 1px solid rgba(236,233,226,0.12); border-radius: 14px; background: #111113; transition: all .25s ease; }
[data-testid="stChatInput"]:focus-within { border-color: rgba(217,164,65,0.6); box-shadow: 0 0 22px rgba(217,164,65,0.14); }

/* ---------- EXPANDER & ALERT ---------- */
[data-testid="stExpander"] { border: 1px solid rgba(236,233,226,0.08); border-radius: 12px; background:#0e0e10; }
[data-testid="stAlert"] { background:#131315; border:1px solid rgba(236,233,226,0.10); border-left:3px solid #d9a441; border-radius:12px; color:#b8b6b0; animation: fadeUp .4s ease both; }

::-webkit-scrollbar { width: 9px; }
::-webkit-scrollbar-thumb { background: linear-gradient(#e0ad4c,#9c6f1f); border-radius: 5px; }

/* ---------- KARTU UNGGAH TENGAH ---------- */
.hero-card { text-align:center; padding:8px 4px 4px; animation: fadeUp .7s ease both; }
.hero-card .em-mark { width:60px; height:60px; margin:0 auto 20px; border-radius:17px; display:grid; place-items:center;
    font-size:28px; color:#0a0a0b; background:linear-gradient(135deg,#f8dd95,#d9a441);
    box-shadow:0 10px 28px rgba(217,164,65,.32); animation: floaty 4.5s ease-in-out infinite; }
.hero-card .em-title { font-family:'Fraunces',serif; font-size:30px; color:#ece9e2; margin-bottom:12px; }
.hero-card .em-sub { font-family:'Inter',sans-serif; font-size:14.5px; color:#b8b6b0; line-height:1.65; max-width:460px; margin:0 auto 6px; }
.hero-card .em-hint { font-family:'Space Mono',monospace; font-size:10.5px; letter-spacing:2px; color:#d9a441; margin-top:20px; margin-bottom:6px; text-transform:uppercase; }
</style>""", unsafe_allow_html=True)

# ================= HERO — gaya Cendekia (obsidian + emas + Fraunces) =================
HERO = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..500&family=Inter:wght@400;500&family=Space+Mono:wght@400;700&display=swap');
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:#0a0a0b; height:300px; position:relative; overflow:hidden; }
.glow { position:absolute; width:640px; height:440px; top:-180px; right:-90px; border-radius:50%;
    background:radial-gradient(circle, rgba(217,164,65,0.12), transparent 60%); animation:pulse 8s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity:.75; transform:scale(1); } 50% { opacity:1; transform:scale(1.06); } }
.rule { position:absolute; left:10px; top:38px; width:38px; height:1px; background:linear-gradient(90deg,#d9a441,transparent); }
.wrap { position:relative; z-index:2; height:100%; display:flex; flex-direction:column; justify-content:center; padding-left:10px; }
.label { font-family:'Space Mono',monospace; font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#d9a441; margin-bottom:18px; opacity:0; animation:rise .8s ease .1s forwards; }
.label .dot { opacity:.5; }
h1 { font-family:'Fraunces',serif; font-size:54px; line-height:1.02; color:#ece9e2; font-weight:400; letter-spacing:.3px; opacity:0; animation:rise .8s ease .25s forwards; }
.type { color:transparent; background:linear-gradient(90deg,#f8dd95,#e0ad4c,#9c6f1f,#f8dd95); background-size:200% auto; -webkit-background-clip:text; background-clip:text; font-style:italic; animation:shine 6s linear infinite; }
@keyframes shine { to { background-position:200% center; } }
.cursor { display:inline-block; width:2px; height:42px; background:#d9a441; margin-left:5px; vertical-align:-8px; box-shadow:0 0 10px #d9a441; animation:blink 0.9s steps(1) infinite; }
@keyframes blink { 50% { opacity:0; } }
.sub { margin-top:18px; color:#b8b6b0; font-size:15px; max-width:560px; line-height:1.6; opacity:0; animation:rise .8s ease .45s forwards; }
@keyframes rise { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
</style></head>
<body>
<div class="glow"></div>
<div class="rule"></div>
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

def proses_file(file):
    """Baca PDF -> potong -> embed -> simpan ke session, lalu segarkan tampilan."""
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
    st.rerun()

# ================= AGEN (Fase 6 — tool-calling) =================
MODEL_AGEN = "llama-3.3-70b-versatile"
MODEL_AGEN_CADANGAN = "llama-3.1-8b-instant"


def cari_dokumen(pertanyaan):
    """Alat: cari potongan relevan di dokumen aktif (RAG)."""
    q = embed([pertanyaan])[0]
    skor = sorted(
        [(kemiripan(q, v), i) for i, v in enumerate(st.session_state.get("vectors", []))],
        reverse=True,
    )[:5]
    return "\n---\n".join(st.session_state.chunks[i] for _, i in skor)


_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _nilai(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_nilai(node.left), _nilai(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_nilai(node.operand))
    raise ValueError("Ekspresi tidak diizinkan")


def hitung(ekspresi):
    """Alat: kalkulator aman untuk ekspresi aritmatika."""
    return str(_nilai(ast.parse(ekspresi, mode="eval").body))


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "cari_dokumen",
            "description": "Cari informasi di dalam dokumen yang diunggah. Gunakan untuk pertanyaan tentang isi dokumen.",
            "parameters": {
                "type": "object",
                "properties": {"pertanyaan": {"type": "string", "description": "Pertanyaan atau kata kunci"}},
                "required": ["pertanyaan"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hitung",
            "description": "Hitung ekspresi matematika, mis. '450000 * 12'.",
            "parameters": {
                "type": "object",
                "properties": {"ekspresi": {"type": "string", "description": "Ekspresi aritmatika"}},
                "required": ["ekspresi"],
            },
        },
    },
]
FUNGSI = {"cari_dokumen": cari_dokumen, "hitung": hitung}

SISTEM_AGEN = """Kamu adalah Agen Riset Cendekia yang cerdas dan teliti.
Pikirkan langkah demi langkah. Untuk pertanyaan tentang isi dokumen, panggil 'cari_dokumen'.
Untuk perhitungan angka, panggil 'hitung'. Kamu boleh memanggil beberapa alat berurutan
(mis. cari harga dulu, lalu hitung totalnya). Jawab HANYA berdasarkan hasil alat; jika tidak
ada di dokumen, katakan dengan jujur. Jawab dalam Bahasa Indonesia yang jelas dan ringkas."""


def _chat_agen(messages):
    for model in (MODEL_AGEN, MODEL_AGEN_CADANGAN):
        try:
            return client.chat.completions.create(
                model=model, messages=messages, tools=TOOLS, temperature=0.2
            )
        except Exception:
            continue
    raise RuntimeError("Gagal memanggil model.")


def jalankan_agen_ui(pertanyaan, maks_langkah=5):
    """Loop agen memakai riwayat percakapan sebagai memori; kembalikan (jawaban, langkah)."""
    messages = [{"role": "system", "content": SISTEM_AGEN}]
    for m in st.session_state.get("messages", []):
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})
    langkah = []
    for _ in range(maks_langkah):
        resp = _chat_agen(messages)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content, langkah
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })
        for tc in msg.tool_calls:
            nama = tc.function.name
            args = {}
            try:
                args = json.loads(tc.function.arguments)
                hasil = FUNGSI[nama](**args)
            except Exception as e:
                hasil = f"Error: {e}"
            langkah.append(f"🔧 {nama}({args}) → {str(hasil).replace(chr(10), ' ')[:80]}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(hasil)})
    return "Maaf, terlalu banyak langkah tanpa jawaban akhir.", langkah


if "messages" not in st.session_state:
    st.session_state.messages = []

aktif = bool(st.session_state.get("nama_file"))

# ================= SIDEBAR (ramping: brand + status) =================
with st.sidebar:
    st.markdown("""<div class="brand">
      <div class="mark">✦</div>
      <div><div class="bname">Cendekia</div><div class="btag">KECERDASAN NUSANTARA</div></div>
    </div>""", unsafe_allow_html=True)
    st.caption("Asisten riset dokumen ber-AI — membaca, memahami, menjawab dengan sumber.")
    st.divider()
    if aktif:
        st.markdown('<div class="sec-label">Dokumen aktif</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="doc-chip"><div class="doc-ic">📄</div>'
            f'<div><div class="doc-l">{st.session_state.get("jumlah", 0)} bagian terindeks</div>'
            f'<div class="doc-n">{st.session_state.nama_file}</div></div></div>',
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("🔄  Ganti dokumen", use_container_width=True):
            for k in ("nama_file", "chunks", "vectors", "jumlah", "messages"):
                st.session_state.pop(k, None)
            st.rerun()
        if st.button("🗑️  Bersihkan percakapan", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.divider()
        st.markdown('<div class="sec-label">Mode</div>', unsafe_allow_html=True)
        st.session_state.mode = st.radio(
            "Mode",
            ["⚡ Tanya Cepat", "🤖 Agen Riset"],
            label_visibility="collapsed",
        )
        st.caption("Agen Riset dapat menghitung & merangkai beberapa langkah otomatis.")
    else:
        st.markdown('<div class="sec-label">Status</div>', unsafe_allow_html=True)
        st.caption("Belum ada dokumen. Unggah PDF di tengah layar untuk memulai.")
    st.divider()
    st.caption("Dibuat oleh Michael Alinskie · Groq + Jina AI")

# ================= AREA TENGAH =================
if not aktif:
    # Kartu unggah di tengah — satu frame rapi
    kiri, tengah, kanan = st.columns([1, 2.1, 1])
    with tengah:
        st.markdown("""<div class="hero-card">
          <div class="em-mark">✦</div>
          <div class="em-title">Mulai dari sebuah dokumen</div>
          <div class="em-sub">Unggah berkas PDF-mu di bawah ini. Cendekia akan membacanya, memahami maknanya, lalu siap menjawab pertanyaanmu — lengkap dengan sumber tepercaya.</div>
          <div class="em-hint">↓ Letakkan atau pilih berkas PDF</div>
        </div>""", unsafe_allow_html=True)
        file = st.file_uploader("Unggah dokumen PDF", type="pdf", label_visibility="collapsed", key="pdf_center")
        if file:
            proses_file(file)
    st.stop()

# ================= CHAT (setelah dokumen aktif) =================
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
    mode = st.session_state.get("mode", "⚡ Tanya Cepat")
    with st.chat_message("assistant"):
        if mode == "🤖 Agen Riset":
            with st.spinner("Agen sedang berpikir & memakai alat..."):
                jawaban, langkah = jalankan_agen_ui(pertanyaan)
            st.markdown(jawaban)
            if langkah:
                with st.expander("Langkah agen"):
                    for baris in langkah:
                        st.caption(baris)
            st.session_state.messages.append({"role": "assistant", "content": jawaban})
        else:
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
