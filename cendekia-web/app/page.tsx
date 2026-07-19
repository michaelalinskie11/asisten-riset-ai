"use client";

import { useState, useRef, useEffect } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Pesan = { role: "user" | "ai"; content: string; sumber?: string[] };

const contoh = [
  "Apa produk utama NusantaraByte?",
  "Siapa CEO dan kapan didirikan?",
  "Berapa harga paket Profesional?",
];

export default function Home() {
  const [pesan, setPesan] = useState<Pesan[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusUpload, setStatusUpload] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [pesan]);

  async function unggah(file: File) {
    setStatusUpload(`⏳ Mengindeks “${file.name}”…`);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (data.status === "ok") {
        setStatusUpload(
          `✅ “${data.nama_file}” terindeks — ${data.jumlah_potongan} potongan siap ditanya.`
        );
      } else {
        setStatusUpload(`⚠️ ${data.pesan || "Gagal mengunggah."}`);
      }
    } catch {
      setStatusUpload("⚠️ Gagal terhubung ke server saat mengunggah.");
    }
  }

  async function kirim(teks: string) {
    const q = teks.trim();
    if (!q || loading) return;
    setInput("");
    setPesan((p) => [
      ...p,
      { role: "user", content: q },
      { role: "ai", content: "" },
    ]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/tanya`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pertanyaan: q }),
      });
      if (!res.ok || !res.body) throw new Error(`Server ${res.status}`);

      // Ambil sumber sitasi dari header (base64 -> JSON)
      let sumber: string[] = [];
      const raw = res.headers.get("X-Sumber");
      if (raw) {
        try {
          const bin = atob(raw);
          const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
          sumber = JSON.parse(new TextDecoder().decode(bytes));
        } catch {
          sumber = [];
        }
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let acc = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });
        setPesan((p) => {
          const s = [...p];
          s[s.length - 1] = { role: "ai", content: acc };
          return s;
        });
      }
      // Setelah selesai, lampirkan sumber
      setPesan((p) => {
        const s = [...p];
        s[s.length - 1] = { role: "ai", content: acc, sumber };
        return s;
      });
    } catch {
      setPesan((p) => {
        const s = [...p];
        s[s.length - 1] = {
          role: "ai",
          content:
            "⚠️ Tidak bisa terhubung ke server.\nPastikan backend berjalan:\n\npython -m uvicorn main:app --reload",
        };
        return s;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="wrap">
      <div className="brand">
        <span className="mark">✦</span>
        <h1 className="title">Cendekia</h1>
      </div>
      <p className="tagline">Kecerdasan yang tenang, jawaban yang bercahaya.</p>

      {/* Upload dokumen */}
      <div className="uploader" onClick={() => fileRef.current?.click()}>
        <input
          ref={fileRef}
          type="file"
          accept="application/pdf"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) unggah(f);
          }}
        />
        <span className="up-ic">⬆️</span>
        <span>Unggah dokumen PDF untuk diindeks</span>
      </div>
      {statusUpload && <div className="up-status">{statusUpload}</div>}

      {/* Chat */}
      <div className="chat">
        {pesan.length === 0 && (
          <div className="empty">
            <div className="big">Tanyakan apa saja tentang dokumenmu.</div>
            <div>Cendekia menjawab berdasarkan dokumen yang telah kamu indeks.</div>
            <div className="chips">
              {contoh.map((c) => (
                <button key={c} className="chip" onClick={() => kirim(c)}>
                  {c}
                </button>
              ))}
            </div>
          </div>
        )}

        {pesan.map((m, i) => {
          const menunggu =
            loading && i === pesan.length - 1 && m.role === "ai" && !m.content;
          return (
            <div key={i} className={`msg ${m.role}`}>
              <div className="avatar">{m.role === "user" ? "🧑" : "✦"}</div>
              <div className="isi">
                <div className={`bubble ${menunggu ? "dot-flash" : ""}`}>
                  {m.content}
                </div>
                {m.sumber && m.sumber.length > 0 && (
                  <details className="sitasi">
                    <summary>📎 {m.sumber.length} sumber dari dokumen</summary>
                    {m.sumber.map((s, idx) => (
                      <div key={idx} className="sitasi-item">
                        <span className="sitasi-no">[{idx + 1}]</span>
                        {s}
                      </div>
                    ))}
                  </details>
                )}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {/* Composer */}
      <div className="composer">
        <form
          className="composer-inner"
          onSubmit={(e) => {
            e.preventDefault();
            kirim(input);
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tulis pertanyaanmu…"
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? "…" : "Kirim"}
          </button>
        </form>
      </div>
    </div>
  );
}
