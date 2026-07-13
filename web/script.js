// =====================================================
//  Cendekia · Quiet Luxury — v2 fitur lengkap
// =====================================================
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const body = document.body;

// ---------- 0. Preloader ----------
const pre = document.getElementById("preloader");
function hidePre() { if (pre) pre.classList.add("done"); }
addEventListener("load", () => setTimeout(hidePre, 1500));
setTimeout(hidePre, 3500);

// ---------- 1. Typing hero ----------
const twPhrases = ["jawaban.", "wawasan.", "ringkasan.", "kejelasan.", "kepastian."];
const twEl = document.getElementById("tw");
let twP = 0, twC = 0, twDel = false;
function twTick() {
  const word = twPhrases[twP];
  twEl.textContent = word.slice(0, twC);
  if (!twDel) { twC++; if (twC > word.length) { twDel = true; setTimeout(twTick, 1500); return; } }
  else { twC--; if (twC < 0) { twDel = false; twC = 0; twP = (twP + 1) % twPhrases.length; } }
  setTimeout(twTick, twDel ? 45 : 95);
}
if (twEl) twTick();

// ---------- 2. JARING-JARING + menyatu jadi GARUDA ----------
const net = document.getElementById("dust");
if (net) {
  const nc = net.getContext("2d");
  let nodes = [], W = innerWidth, H = innerHeight;
  const mouse = { x: -9999, y: -9999 };
  let formPts = [], formReady = false;

  (function buildForm() {
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 172"><g fill="#fff">'
      + '<path d="M100,26 L82,4 L92,22 L100,1 L108,22 L118,4 Z"/>'
      + '<circle cx="100" cy="35" r="15"/>'
      + '<path d="M80,52 Q100,40 120,52 Q127,100 100,132 Q73,100 80,52 Z"/>'
      + '<path d="M82,58 Q36,22 2,16 Q24,48 56,62 Q70,68 82,70 Z"/>'
      + '<path d="M82,69 Q34,44 4,42 Q28,68 64,80 Q76,82 82,82 Z"/>'
      + '<path d="M81,81 Q40,64 12,66 Q38,88 70,96 Q78,96 81,94 Z"/>'
      + '<path d="M80,94 Q46,80 22,82 Q46,102 72,106 Q78,106 80,104 Z"/>'
      + '<path d="M118,58 Q164,22 198,16 Q176,48 144,62 Q130,68 118,70 Z"/>'
      + '<path d="M118,69 Q166,44 196,42 Q172,68 136,80 Q124,82 118,82 Z"/>'
      + '<path d="M119,81 Q160,64 188,66 Q162,88 130,96 Q122,96 119,94 Z"/>'
      + '<path d="M120,94 Q154,80 178,82 Q154,102 128,106 Q122,106 120,104 Z"/>'
      + '<path d="M91,126 Q100,120 109,126 L105,168 Q100,174 95,168 Z"/>'
      + '</g></svg>';
    const img = new Image();
    img.onload = () => {
      const fw = 150, fh = Math.round(150 * 172 / 200);
      const off = document.createElement("canvas"); off.width = fw; off.height = fh;
      const o = off.getContext("2d"); o.drawImage(img, 0, 0, fw, fh);
      let d; try { d = o.getImageData(0, 0, fw, fh).data; } catch (e) { return; }
      const pts = [];
      for (let y = 0; y < fh; y += 2) for (let x = 0; x < fw; x += 2)
        if (d[(y * fw + x) * 4 + 3] > 128) pts.push({ nx: x / fw, ny: y / fh });
      if (pts.length) { formPts = pts; formReady = true; layoutForm(); }
    };
    img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  })();

  function layoutForm() {
    if (!formReady || !nodes.length) return;
    const boxH = Math.min(H * 0.52, 500), boxW = boxH * 200 / 172;
    const ox = (W - boxW) / 2, oy = (H - boxH) / 2 * 0.86;
    for (let i = 0; i < nodes.length; i++) {
      const fp = formPts[Math.floor(i / nodes.length * formPts.length) % formPts.length];
      nodes[i].tx = ox + fp.nx * boxW; nodes[i].ty = oy + fp.ny * boxH;
    }
  }
  function netResize() {
    const DPR = Math.min(2, devicePixelRatio || 1);
    W = innerWidth; H = innerHeight;
    net.width = W * DPR; net.height = H * DPR; nc.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  function netInit() {
    nodes = [];
    const n = Math.min(95, Math.max(34, Math.round(W * H / 15000)));
    for (let i = 0; i < n; i++) nodes.push({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.26, vy: (Math.random() - 0.5) * 0.26,
      r: Math.random() * 1.2 + 0.6, tx: null, ty: null, rx: 0, ry: 0,
    });
    layoutForm();
  }
  netResize(); netInit();
  addEventListener("mousemove", (e) => { mouse.x = e.clientX; mouse.y = e.clientY; });
  addEventListener("mouseout", () => { mouse.x = -9999; mouse.y = -9999; });
  addEventListener("resize", () => { netResize(); netInit(); });

  const LINK = 138, MLINK = 190;
  const canForm = () => formReady && !reduce && W > 760;
  const easeIO = (t) => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;

  function draw(now) {
    nc.clearRect(0, 0, W, H);
    let amt = 0;
    if (canForm()) {
      const cyc = (now % 15000) / 15000;
      if (cyc > 0.42 && cyc < 0.86) {
        const seg = (cyc - 0.42) / 0.44;
        let a = seg < 0.22 ? seg / 0.22 : seg > 0.78 ? (1 - seg) / 0.22 : 1;
        amt = easeIO(Math.max(0, Math.min(1, a)));
      }
    }
    for (const p of nodes) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
      p.rx = p.tx != null ? p.x + (p.tx - p.x) * amt : p.x;
      p.ry = p.ty != null ? p.y + (p.ty - p.y) * amt : p.y;
    }
    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        const dx = a.rx - b.rx, dy = a.ry - b.ry, d = Math.hypot(dx, dy);
        if (d < LINK) {
          const al = (1 - d / LINK) * (0.18 + 0.32 * amt);
          nc.strokeStyle = amt > 0.4
            ? "rgba(217,164,65," + al.toFixed(3) + ")"
            : "rgba(190,186,178," + al.toFixed(3) + ")";
          nc.lineWidth = 0.6;
          nc.beginPath(); nc.moveTo(a.rx, a.ry); nc.lineTo(b.rx, b.ry); nc.stroke();
        }
      }
      if (amt < 0.4) {
        const mdx = a.rx - mouse.x, mdy = a.ry - mouse.y, md = Math.hypot(mdx, mdy);
        if (md < MLINK) {
          const al = (1 - md / MLINK) * 0.42 * (1 - amt);
          nc.strokeStyle = "rgba(217,164,65," + al.toFixed(3) + ")";
          nc.lineWidth = 0.7;
          nc.beginPath(); nc.moveTo(a.rx, a.ry); nc.lineTo(mouse.x, mouse.y); nc.stroke();
        }
      }
    }
    for (const p of nodes) {
      nc.beginPath(); nc.arc(p.rx, p.ry, p.r + amt * 0.6, 0, 6.2832);
      nc.fillStyle = "rgba(214,180,110," + (0.5 + 0.45 * amt).toFixed(3) + ")"; nc.fill();
    }
  }
  if (!reduce) { (function loop(t) { draw(t || 0); requestAnimationFrame(loop); })(); }
  else draw(0);
}

// ---------- 3. Demo chat + "coba sendiri" ----------
const chat = document.getElementById("chat");
const askForm = document.getElementById("askForm");
const askInput = document.getElementById("askInput");
let userMode = false, chatTimers = [];
const convos = [
  { q: "Kapan NusantaraByte didirikan?", a: "NusantaraByte didirikan pada tahun 2023 di Surabaya.", c: "dokumen.pdf · hal. 1" },
  { q: "Berapa harga paket Pelajar?", a: "Paket Pelajar tersedia seharga Rp150.000 per bulan.", c: "dokumen.pdf · hal. 2" },
  { q: "Apa target pengguna akhir 2026?", a: "Targetnya mencapai 30.000 pengguna aktif bulanan.", c: "dokumen.pdf · hal. 4" },
];
const KB = [
  { k: ["didirikan", "berdiri", "kapan", "tahun", "2023"], a: "NusantaraByte didirikan pada tahun 2023 di Surabaya.", c: "dokumen.pdf · hal. 1" },
  { k: ["ceo", "pendiri", "pimpinan"], a: "CEO NusantaraByte adalah Michael Alinskie.", c: "dokumen.pdf · hal. 1" },
  { k: ["produk", "lontara"], a: "Produk utamanya adalah Lontara AI.", c: "dokumen.pdf · hal. 1" },
  { k: ["pelajar", "150"], a: "Paket Pelajar seharga Rp150.000 per bulan.", c: "dokumen.pdf · hal. 2" },
  { k: ["profesional", "450"], a: "Paket Profesional seharga Rp450.000 per bulan.", c: "dokumen.pdf · hal. 2" },
  { k: ["gratis", "free"], a: "Tersedia paket Gratis seharga Rp0.", c: "dokumen.pdf · hal. 2" },
  { k: ["harga", "paket", "biaya", "langganan", "berapa"], a: "Ada tiga paket: Gratis (Rp0), Pelajar (Rp150.000), dan Profesional (Rp450.000) per bulan.", c: "dokumen.pdf · hal. 2" },
  { k: ["pengguna", "mau", "target", "30.000", "30000"], a: "Targetnya 30.000 pengguna aktif bulanan pada akhir 2026.", c: "dokumen.pdf · hal. 4" },
  { k: ["alamat", "lokasi", "kantor", "dimana", "surabaya"], a: "Kantornya berada di Jalan Pemuda No. 88, Surabaya.", c: "dokumen.pdf · hal. 3" },
  { k: ["bahasa", "jawa", "bali"], a: "Dukungan bahasa Jawa & Bali direncanakan pada Q4 2026.", c: "dokumen.pdf · hal. 4" },
  { k: ["lintas", "cross", "q3"], a: "Fitur lintas-dokumen direncanakan hadir pada Q3 2026.", c: "dokumen.pdf · hal. 4" },
];
let ci = 0;
function clearChatTimers() { chatTimers.forEach(clearTimeout); chatTimers = []; }
function later(fn, ms) { const t = setTimeout(fn, ms); chatTimers.push(t); return t; }
function typeInto(el, text, speed, done) {
  let i = 0;
  (function tk() { el.textContent = text.slice(0, i); i++; if (i <= text.length) later(tk, speed); else done && done(); })();
}
function streamAnswer(text, cite, speed) {
  const ai = document.createElement("div"); ai.className = "bubble ai";
  const think = document.createElement("span"); think.className = "think";
  think.innerHTML = "<i></i><i></i><i></i>"; ai.appendChild(think); chat.appendChild(ai);
  return later(() => {
    ai.innerHTML = ""; const txt = document.createElement("span"); ai.appendChild(txt);
    const words = text.split(" "); let wi = 0;
    (function stream() {
      txt.textContent = words.slice(0, wi).join(" "); wi++;
      if (wi <= words.length) later(stream, speed);
      else {
        const c = document.createElement("span"); c.className = "cite";
        c.textContent = "\uD83D\uDCC4 " + cite;
        ai.appendChild(document.createElement("br")); ai.appendChild(c);
        if (!userMode) { ci = (ci + 1) % convos.length; later(runDemo, 2800); }
      }
    })();
  }, 1100);
}
function runDemo() {
  if (!chat || userMode) return;
  clearChatTimers(); chat.innerHTML = "";
  const { q, a, c } = convos[ci];
  const u = document.createElement("div"); u.className = "bubble user"; chat.appendChild(u);
  typeInto(u, q, 50, () => later(() => streamAnswer(a, c, 85), 400));
}
if (chat) later(runDemo, 900);
function answerFor(q) {
  const s = q.toLowerCase(); let best = null, score = 0;
  for (const it of KB) { let sc = 0; for (const k of it.k) if (s.includes(k)) sc++; if (sc > score) { score = sc; best = it; } }
  if (best && score > 0) return best;
  return { a: "Ini demo dengan satu dokumen contoh, jadi jawabanku terbatas. Versi lengkap Cendekia membaca dokumen aslimu — coba langsung di aplikasi.", c: "mode demo" };
}
if (askForm) askForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = (askInput.value || "").trim(); if (!q) return;
  userMode = true; clearChatTimers(); chat.innerHTML = ""; askInput.value = "";
  const it = answerFor(q);
  const u = document.createElement("div"); u.className = "bubble user"; u.textContent = q; chat.appendChild(u);
  later(() => streamAnswer(it.a, it.c, 70), 350);
});

// ---------- 4. Tilt kartu ----------
const tilt = document.getElementById("tiltcard");
if (tilt && !reduce) {
  tilt.addEventListener("mousemove", (e) => {
    const r = tilt.getBoundingClientRect();
    const rx = ((e.clientY - r.top) / r.height - 0.5) * -6;
    const ry = ((e.clientX - r.left) / r.width - 0.5) * 6;
    tilt.style.transform = "rotateX(" + rx + "deg) rotateY(" + ry + "deg)";
  });
  tilt.addEventListener("mouseleave", () => { tilt.style.transform = ""; });
}

// ---------- 5. Filosofi split ----------
const accent = new Set(["tenang,", "jujur,", "bersumber."]);
document.querySelectorAll("[data-split]").forEach((el) => {
  const words = el.textContent.trim().split(/\s+/);
  el.innerHTML = words.map((wd, i) => {
    const gg = accent.has(wd) ? " g" : "";
    return '<span class="w' + gg + '"><span style="transition-delay:' + (i * 0.03).toFixed(2) + 's">' + wd + "</span></span>";
  }).join(" ");
});

// ---------- 6. Tombol magnetik ----------
document.querySelectorAll(".magnet").forEach((b) => {
  b.addEventListener("mousemove", (e) => {
    const r = b.getBoundingClientRect();
    b.style.transform = "translate(" + (e.clientX - r.left - r.width / 2) * 0.28 + "px," +
      (e.clientY - r.top - r.height / 2) * 0.4 + "px)";
  });
  b.addEventListener("mouseleave", () => { b.style.transform = ""; });
});

// ---------- 7. Statistik menghitung ----------
function startCounts(sec) {
  sec.querySelectorAll(".val").forEach((el) => {
    if (el._run) return; el._run = true;
    const to = parseFloat(el.dataset.to), dec = parseInt(el.dataset.dec || "0"), dur = 1500;
    let s = null;
    function step(ts) {
      if (!s) s = ts;
      const p = Math.min(1, (ts - s) / dur);
      el.textContent = (to * (1 - Math.pow(1 - p, 3))).toFixed(dec);
      if (p < 1) requestAnimationFrame(step); else el.textContent = to.toFixed(dec);
    }
    requestAnimationFrame(step);
  });
}
function resetCounts(sec) { sec.querySelectorAll(".val").forEach((el) => { el._run = false; el.textContent = "0"; }); }

// ---------- 8. Scramble ----------
function runScramble(el) {
  if (!el.dataset.text) el.dataset.text = el.textContent;
  const final = el.dataset.text;
  const glyphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&/<>*";
  const start = performance.now(), dur = 760;
  function tick(now) {
    const p = Math.min(1, (now - start) / dur); let out = "";
    for (let i = 0; i < final.length; i++) {
      const ch = final[i];
      if (ch === " ") { out += " "; continue; }
      const th = (i / final.length) * 0.6;
      out += (p >= th + 0.22) ? ch : glyphs[(Math.random() * glyphs.length) | 0];
    }
    el.textContent = out;
    if (p < 1) requestAnimationFrame(tick); else el.textContent = final;
  }
  requestAnimationFrame(tick);
}

// ---------- 9. Peta ruang-vektor ----------
const VCHUNKS = [
  { t: "NusantaraByte didirikan pada 2023 di Surabaya.", hot: true },
  { t: "Paket Pelajar: Rp150.000 per bulan.", hot: true },
  { t: "Target 30.000 pengguna aktif bulanan akhir 2026.", hot: true },
  { t: "CEO: Michael Alinskie.", hot: false },
  { t: "Produk utama: Lontara AI.", hot: false },
  { t: "Paket Profesional: Rp450.000 per bulan.", hot: false },
  { t: "Paket Gratis: Rp0.", hot: false },
  { t: "Alamat: Jalan Pemuda No. 88, Surabaya.", hot: false },
  { t: "Dukungan bahasa Jawa & Bali — Q4 2026.", hot: false },
  { t: "Fitur lintas-dokumen — Q3 2026.", hot: false },
  { t: "Visi: pengetahuan yang mudah dijangkau.", hot: false },
  { t: "Segmen: pelajar & profesional.", hot: false },
  { t: "Model bahasa dijalankan via Groq.", hot: false },
  { t: "Embedding teks memakai Jina AI.", hot: false },
  { t: "Konteks pendukung dokumen.", hot: false },
  { t: "Metadata halaman & sumber.", hot: false },
  { t: "Ringkasan bagian pendahuluan.", hot: false },
  { t: "Catatan kaki & referensi.", hot: false },
  { t: "Konteks pendukung dokumen.", hot: false },
  { t: "Bagian lampiran teknis.", hot: false },
];
function buildVmap(vm) {
  const tip = document.createElement("div"); tip.className = "vtip"; vm.appendChild(tip);
  VCHUNKS.forEach((c) => {
    const ang = Math.random() * 6.2832;
    const rad = c.hot ? (Math.random() * 14 + 6) : (Math.random() * 30 + 26);
    const x = 50 + Math.cos(ang) * rad;
    const y = 50 + Math.sin(ang) * rad * 0.92;
    const dot = document.createElement("div");
    dot.className = "vdot" + (c.hot ? " hot" : "");
    dot.style.left = x + "%"; dot.style.top = y + "%";
    dot.addEventListener("mouseenter", () => {
      tip.textContent = c.t; tip.style.left = x + "%"; tip.style.top = y + "%";
      tip.classList.add("show");
    });
    dot.addEventListener("mouseleave", () => tip.classList.remove("show"));
    vm.appendChild(dot);
  });
  // titik query di tengah
  const q = document.createElement("div"); q.className = "vquery"; q.style.left = "50%"; q.style.top = "50%";
  q.textContent = "kueri"; vm.appendChild(q);
}

// ---------- 10. Reveal dua arah ----------
const revealEls = [...document.querySelectorAll("[data-anim], .mask-reveal, .statement, .stats, [data-scramble], .flow, .vmap, .beam")];
function checkReveal() {
  const vh = innerHeight;
  for (const el of revealEls) {
    const r = el.getBoundingClientRect();
    const vis = r.top < vh * 0.84 && r.bottom > vh * 0.16;
    if (vis && !el._shown) {
      el._shown = true; el.classList.add("show");
      if (el.classList.contains("flow")) el.classList.add("play");
      if (el.classList.contains("stats")) startCounts(el);
      if (el.classList.contains("vmap") && !el._built) { el._built = true; buildVmap(el); }
      if (el.dataset.scramble !== undefined) runScramble(el);
    } else if (!vis && el._shown) {
      el._shown = false; el.classList.remove("show");
      if (el.classList.contains("flow")) el.classList.remove("play");
      if (el.classList.contains("stats")) resetCounts(el);
    }
  }
}

// ---------- 10b. Dari bising jadi jelas ----------
const beam = document.getElementById("beam");
if (beam) {
  const noise = beam.querySelector(".noise");
  for (let i = 0; i < 16; i++) {
    const b = document.createElement("i");
    const w = 28 + Math.random() * 46;
    b.style.width = w + "%";
    b.style.left = (Math.random() * (96 - w)) + "%";
    b.style.top = (5 + Math.random() * 88) + "%";
    b.style.transitionDelay = (Math.random() * 0.5).toFixed(2) + "s";
    noise.appendChild(b);
  }
}

// ---------- 10c. Sorotan Pemahaman + cahaya kejelasan ----------
const clarity = document.getElementById("clarity");
const readerDoc = document.getElementById("readerDoc");
const rrows = readerDoc ? [...readerDoc.querySelectorAll(".rrow")] : [];
function updateReader() {
  if (!readerDoc || !rrows.length) return;
  const r = readerDoc.getBoundingClientRect();
  const p = (innerHeight * 0.72 - r.top) / (r.height * 0.6);
  const active = Math.max(0, Math.min(rrows.length, Math.round(p * rrows.length)));
  for (let i = 0; i < rrows.length; i++) rrows[i].classList.toggle("on", i < active);
}

// ---------- 11. Smooth scroll + progres ----------
const sc = document.getElementById("scroll-content");
const progress = document.getElementById("progress");
let current = 0, target = 0, maxScroll = 1;
function setBodyHeight() {
  const h = Math.ceil(sc.getBoundingClientRect().height);
  document.body.style.height = h + "px";
  maxScroll = Math.max(1, h - innerHeight);
}
if (!reduce) {
  document.body.classList.add("smooth");
  setBodyHeight();
  addEventListener("load", setBodyHeight);
  addEventListener("resize", setBodyHeight);
  setTimeout(setBodyHeight, 700);
} else { maxScroll = Math.max(1, document.body.scrollHeight - innerHeight); }
(function loop() {
  target = scrollY;
  if (document.body.classList.contains("smooth")) {
    current += (target - current) * 0.085;
    if (Math.abs(target - current) < 0.06) current = target;
    sc.style.transform = "translate3d(0," + (-current) + "px,0)";
  } else current = target;
  const sp = Math.min(1, target / maxScroll);
  progress.style.transform = "scaleX(" + sp + ")";
  if (clarity) clarity.style.opacity = (sp * 0.9).toFixed(3);
  updateReader();
  checkReveal();
  requestAnimationFrame(loop);
})();

// ---------- 12. Navigasi halus (dipakai anchor + ⌘K) ----------
function goTo(sel) {
  if (sel === "#top") { scrollTo({ top: 0, behavior: body.classList.contains("smooth") ? "auto" : "smooth" }); return; }
  const el = document.querySelector(sel); if (!el) return;
  const y = el.getBoundingClientRect().top + current - 80;
  scrollTo({ top: y, behavior: body.classList.contains("smooth") ? "auto" : "smooth" });
}
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener("click", (e) => {
    const id = a.getAttribute("href"); if (id.length < 2) return;
    if (!document.querySelector(id)) return;
    e.preventDefault(); goTo(id);
  });
});

// ---------- 13. Command palette ⌘K ----------
const cmdk = document.getElementById("cmdk");
const cmdkInput = document.getElementById("cmdkInput");
const cmdkList = document.getElementById("cmdkList");
const cmdkHint = document.getElementById("cmdkHint");
const CMDS = [
  { label: "Dipercaya", k: "01", act: () => goTo("#performa") },
  { label: "Filosofi", k: "02", act: () => goTo("#filosofi") },
  { label: "Dari bising jadi jelas", k: "03", act: () => goTo("#jelas") },
  { label: "Fitur", k: "04", act: () => goTo("#fitur") },
  { label: "Cara Kerja", k: "05", act: () => goTo("#cara") },
  { label: "Di Balik Layar · RAG", k: "06", act: () => goTo("#ragstory") },
  { label: "Sorotan Pemahaman", k: "07", act: () => goTo("#baca") },
  { label: "Peta Ruang-Vektor", k: "08", act: () => goTo("#vektor") },
  { label: "Mode tanya layar penuh", k: "\u2922", act: () => openFs() },
  { label: "Tanya Cendekia sekarang", k: "\u21B5", act: () => { goTo("#top"); setTimeout(() => askInput && askInput.focus(), 450); } },
  { label: "Masuk Aplikasi", k: "\u2197", act: () => window.open("https://ISI-LINK-STREAMLIT-MU.streamlit.app", "_blank") },
];
let cmdkActive = 0, cmdkFiltered = CMDS.slice();
function renderCmd() {
  cmdkList.innerHTML = "";
  cmdkFiltered.forEach((c, i) => {
    const li = document.createElement("li");
    if (i === cmdkActive) li.className = "active";
    li.innerHTML = "<span>" + c.label + '</span><span class="k">' + c.k + "</span>";
    li.addEventListener("click", () => { runCmd(c); });
    li.addEventListener("mousemove", () => { cmdkActive = i; paintActive(); });
    cmdkList.appendChild(li);
  });
}
function paintActive() {
  [...cmdkList.children].forEach((li, i) => li.className = i === cmdkActive ? "active" : "");
}
function filterCmd(q) {
  const s = q.toLowerCase().trim();
  cmdkFiltered = s ? CMDS.filter((c) => c.label.toLowerCase().includes(s)) : CMDS.slice();
  cmdkActive = 0; renderCmd();
}
function openCmd() { if (!cmdk) return; cmdk.classList.add("open"); cmdkInput.value = ""; filterCmd(""); setTimeout(() => cmdkInput.focus(), 60); }
function closeCmd() { if (cmdk) cmdk.classList.remove("open"); }
function runCmd(c) { closeCmd(); if (c && c.act) c.act(); }
if (cmdk) {
  cmdkHint && cmdkHint.addEventListener("click", openCmd);
  cmdkInput.addEventListener("input", (e) => filterCmd(e.target.value));
  addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); cmdk.classList.contains("open") ? closeCmd() : openCmd(); return; }
    if (!cmdk.classList.contains("open")) return;
    if (e.key === "Escape") closeCmd();
    else if (e.key === "ArrowDown") { e.preventDefault(); cmdkActive = Math.min(cmdkFiltered.length - 1, cmdkActive + 1); paintActive(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); cmdkActive = Math.max(0, cmdkActive - 1); paintActive(); }
    else if (e.key === "Enter") { e.preventDefault(); runCmd(cmdkFiltered[cmdkActive]); }
  });
  cmdk.addEventListener("click", (e) => { if (e.target === cmdk) closeCmd(); });
}

// ---------- 15. Mode tanya layar penuh ----------
const chatfs = document.getElementById("chatfs");
const chatfsBody = document.getElementById("chatfsBody");
const chatfsForm = document.getElementById("chatfsForm");
const chatfsInput = document.getElementById("chatfsInput");
const chatfsChips = document.getElementById("chatfsChips");
const cardExpand = document.getElementById("cardExpand");
const chatfsClose = document.getElementById("chatfsClose");
const SUGGEST = ["Kapan NusantaraByte didirikan?", "Berapa harga paket Pelajar?", "Siapa CEO-nya?", "Apa target akhir 2026?", "Di mana kantornya?"];
function fsUser(q) {
  const u = document.createElement("div"); u.className = "bubble user"; u.textContent = q;
  chatfsBody.appendChild(u); chatfsBody.scrollTop = chatfsBody.scrollHeight;
}
function fsStream(text, cite) {
  const ai = document.createElement("div"); ai.className = "bubble ai";
  const think = document.createElement("span"); think.className = "think"; think.innerHTML = "<i></i><i></i><i></i>";
  ai.appendChild(think); chatfsBody.appendChild(ai); chatfsBody.scrollTop = chatfsBody.scrollHeight;
  setTimeout(() => {
    ai.innerHTML = ""; const txt = document.createElement("span"); ai.appendChild(txt);
    const words = text.split(" "); let wi = 0;
    (function s() {
      txt.textContent = words.slice(0, wi).join(" "); wi++; chatfsBody.scrollTop = chatfsBody.scrollHeight;
      if (wi <= words.length) setTimeout(s, 55);
      else {
        const c = document.createElement("span"); c.className = "cite"; c.textContent = "\uD83D\uDCC4 " + cite;
        ai.appendChild(document.createElement("br")); ai.appendChild(c); chatfsBody.scrollTop = chatfsBody.scrollHeight;
      }
    })();
  }, 700);
}
function fsAsk(q) { fsUser(q); const it = answerFor(q); setTimeout(() => fsStream(it.a, it.c), 320); }
function openFs() {
  if (!chatfs) return;
  chatfs.classList.add("open"); chatfs.setAttribute("aria-hidden", "false");
  if (!chatfsBody.dataset.init) {
    chatfsBody.dataset.init = "1";
    fsStream("Halo! Aku Cendekia. Tanyakan apa saja tentang dokumen contoh \u2014 aku jawab lengkap dengan sumbernya.", "mode demo");
  }
  setTimeout(() => chatfsInput && chatfsInput.focus(), 140);
}
function closeFs() { if (chatfs) { chatfs.classList.remove("open"); chatfs.setAttribute("aria-hidden", "true"); } }
if (chatfsChips) SUGGEST.forEach((s) => {
  const b = document.createElement("button"); b.textContent = s;
  b.addEventListener("click", () => fsAsk(s)); chatfsChips.appendChild(b);
});
if (cardExpand) cardExpand.addEventListener("click", openFs);
if (chatfsClose) chatfsClose.addEventListener("click", closeFs);
if (chatfs) chatfs.addEventListener("click", (e) => { if (e.target === chatfs) closeFs(); });
if (chatfsForm) chatfsForm.addEventListener("submit", (e) => {
  e.preventDefault(); const q = (chatfsInput.value || "").trim(); if (!q) return;
  chatfsInput.value = ""; fsAsk(q);
});
addEventListener("keydown", (e) => { if (e.key === "Escape") closeFs(); });
