"use client";

/*
 * Cendekia — Beranda
 * Referensi: noth.in (studio Paris).
 *
 * Hero (halaman atas) — DUA LAYER "minyak & air":
 *   LAYER DEPAN : CENDEKIA hitam di atas background putih.
 *   LAYER BELAKANG: CENDEKIA 3D (ekstrusi + bevel + gloss). Tiap ~2.4 dtk
 *                   FONT dan WARNA berganti (crossfade) mengikuti siklus asli
 *                   noth.in: wine-red → rose → teal → bronze → taupe.
 *   PERCIKAN AIR: sistem partikel — tetesan dipancarkan sepanjang jejak kursor,
 *                 memercik keluar (splash), membesar lalu mengecil, dan menyatu
 *                 lewat filter gooey; menumpuk & menyebar saat digerakkan lalu
 *                 surut kembali ke putih saat diam (kurva noth.in).
 *
 * Palet, siklus warna & dinamika percikan diukur dari video noth.in.
 */

import React, { useEffect, useRef, useState } from "react";
import Lenis from "lenis";
import dynamic from "next/dynamic";

/* ------------------------------------------------------------------ *
 *  Robot 3D (Spline)
 * ------------------------------------------------------------------ */
const SplineScene = dynamic(() => import("@splinetool/react-spline"), {
  ssr: false,
  loading: () => <div className="spline-load">memuat robot 3D…</div>,
});
function SplineRobot() {
  return <SplineScene scene="/scene.splinecode" className="spline-robot" />;
}

function RobotStage() {
  return (
    <section className="robot-stage" id="asisten">
      <div className="robot-sticky">
        <div className="robot-glow" />
        <div className="robot-canvas">
          <SplineRobot />
        </div>
        <div className="robot-copy">
          <span className="seksi-label light">02 — Asisten</span>
          <h2 className="robot-h">Kecerdasan yang menatapmu.</h2>
          <p className="robot-sub">
            Gerakkan kursor — matanya mengikuti ke mana pun kamu memandang.
          </p>
          <a className="robot-cta" href="/">
            Coba Cendekia <span aria-hidden>→</span>
          </a>
        </div>
        <span className="robot-hint">Arahkan kursor ke robot</span>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ *
 *  Reveal helpers
 * ------------------------------------------------------------------ */
function Judul({ text, className = "" }: { text: string; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setVis(true);
          io.disconnect();
        }
      },
      { threshold: 0.2 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  const lines = text.split("\n");
  let k = 0;
  return (
    <div ref={ref} className={`mask-wrap ${vis ? "in" : ""} ${className}`}>
      {lines.map((ln, li) => (
        <span className="mask-line" key={li}>
          {ln.split(" ").map((w, wi) => {
            const d = k++ * 55;
            return (
              <span className="mask" key={wi}>
                <span className="word" style={{ transitionDelay: `${d}ms` }}>
                  {w}
                </span>
              </span>
            );
          })}
        </span>
      ))}
    </div>
  );
}

function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setVis(true);
          io.disconnect();
        }
      },
      { threshold: 0.15 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <div
      ref={ref}
      className={`reveal ${vis ? "in" : ""} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

const FITUR = [
  {
    no: "01",
    judul: "Riset Dokumen",
    teks: "Pahami dokumen apa pun dalam hitungan detik.",
  },
  {
    no: "02",
    judul: "Sitasi Tepercaya",
    teks: "Setiap jawaban berpijak pada sumber nyata.",
  },
  {
    no: "03",
    judul: "Multi-Dokumen",
    teks: "Bandingkan banyak sumber sekaligus.",
  },
  {
    no: "04",
    judul: "Memori Permanen",
    teks: "Riwayat riset tersimpan aman dan rapi.",
  },
];
function GaleriPinned() {
  const pin = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let raf = 0;
    const tick = () => {
      const el = pin.current;
      const tr = track.current;
      if (el && tr) {
        const total = el.offsetHeight - window.innerHeight;
        const p = Math.min(
          1,
          Math.max(0, -el.getBoundingClientRect().top / (total || 1)),
        );
        const dist = tr.scrollWidth - window.innerWidth + 72;
        tr.style.transform = `translate3d(${-p * dist}px,0,0)`;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);
  return (
    <section className="pin" ref={pin} id="fitur">
      <div className="pin-sticky">
        <div className="track" ref={track}>
          <div className="kartu kartu-intro">
            <span className="seksi-label">03 — Kemampuan</span>
            <h2 className="kartu-intro-h">
              Empat cara
              <br />
              Cendekia
              <br />
              membantumu.
            </h2>
          </div>
          {FITUR.map((f) => (
            <div className="kartu" key={f.no}>
              <span className="kartu-no">{f.no}</span>
              <h3 className="kartu-judul">{f.judul}</h3>
              <p className="kartu-teks">{f.teks}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* Siklus warna — nada asli dari histogram noth.in (satu font balon) */
const PHASES = ["gRed", "gRose", "gTeal", "gBronze", "gTaupe"];

/* ================================================================== *
 *  BERANDA
 * ================================================================== */
export default function Beranda() {
  const lenisRef = useRef<Lenis | null>(null);
  const counter = useRef<HTMLSpanElement>(null);
  const loaderNum = useRef<HTMLSpanElement>(null);
  const dotRef = useRef<HTMLDivElement>(null);
  const heroTitleRef = useRef<HTMLDivElement>(null);
  const heroSvgRef = useRef<SVGSVGElement>(null);
  const baseRef = useRef<SVGTextElement>(null);
  const phaseRefs = useRef<Array<SVGGElement | null>>([]);
  const scaleGroupRef = useRef<SVGGElement>(null);
  const dispRef = useRef<SVGFEDisplacementMapElement>(null);
  const blobRef = useRef<SVGGElement>(null);
  const [loaded, setLoaded] = useState(false);
  const [menu, setMenu] = useState(false);

  // Smooth scroll (Lenis) + progress counter
  useEffect(() => {
    const lenis = new Lenis({ lerp: 0.08, smoothWheel: true });
    lenisRef.current = lenis;
    lenis.stop();
    let raf = 0;
    const loop = (t: number) => {
      lenis.raf(t);
      const p = (lenis as unknown as { progress: number }).progress || 0;
      if (counter.current)
        counter.current.textContent = String(Math.round(p * 100)).padStart(
          3,
          "0",
        );
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => {
      cancelAnimationFrame(raf);
      lenis.destroy();
    };
  }, []);

  // Preloader 000 → 100
  useEffect(() => {
    const start = performance.now();
    const dur = 2200;
    let raf = 0;
    const step = (t: number) => {
      const p = Math.min(1, (t - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      if (loaderNum.current)
        loaderNum.current.textContent = String(
          Math.round(eased * 100),
        ).padStart(3, "0");
      if (p < 1) raf = requestAnimationFrame(step);
      else setTimeout(() => setLoaded(true), 650);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, []);

  useEffect(() => {
    const l = lenisRef.current;
    if (!l) return;
    if (loaded && !menu) l.start();
    else l.stop();
  }, [loaded, menu]);

  // Kursor: titik hitam kecil yang mengikuti mouse dengan halus
  useEffect(() => {
    const dot = dotRef.current;
    if (!dot) return;
    let x = window.innerWidth / 2,
      y = window.innerHeight / 2,
      tx = x,
      ty = y,
      raf = 0;
    const move = (e: MouseEvent) => {
      tx = e.clientX;
      ty = e.clientY;
    };
    const loop = () => {
      x += (tx - x) * 0.35;
      y += (ty - y) * 0.35;
      dot.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`;
      raf = requestAnimationFrame(loop);
    };
    window.addEventListener("mousemove", move);
    raf = requestAnimationFrame(loop);
    return () => {
      window.removeEventListener("mousemove", move);
      cancelAnimationFrame(raf);
    };
  }, []);

  // Efek magnetic pada elemen .magnetic
  useEffect(() => {
    const els = Array.from(
      document.querySelectorAll(".magnetic"),
    ) as HTMLElement[];
    const cleanups: Array<() => void> = [];
    els.forEach((el) => {
      const mm = (e: MouseEvent) => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - (r.left + r.width / 2);
        const y = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
      };
      const ml = () => {
        el.style.transform = "translate(0,0)";
      };
      el.addEventListener("mousemove", mm);
      el.addEventListener("mouseleave", ml);
      cleanups.push(() => {
        el.removeEventListener("mousemove", mm);
        el.removeEventListener("mouseleave", ml);
      });
    });
    return () => cleanups.forEach((c) => c());
  }, []);

  /* ---------------------------------------------------------------- *
   *  HERO — PERCIKAN AIR (partikel) + chrome 3D font/warna berganti.
   * ---------------------------------------------------------------- */
  useEffect(() => {
    const svg = heroSvgRef.current,
      base = baseRef.current,
      blobG = blobRef.current,
      scaleG = scaleGroupRef.current,
      title = heroTitleRef.current;
    if (!svg || !base || !blobG || !scaleG || !title) return;
    const NS = "http://www.w3.org/2000/svg";
    const TAU = Math.PI * 2;
    const CORE = 5;
    const SPLASH = 46;
    const N = CORE + SPLASH;
    const circ: SVGCircleElement[] = [];
    for (let i = 0; i < N; i++) {
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("fill", "#fff");
      c.setAttribute("cx", "-999");
      c.setAttribute("cy", "-999");
      c.setAttribute("r", "0");
      blobG.appendChild(c);
      circ.push(c);
    }
    const VB = { x: 0, y: 0, w: 100, h: 100 };
    let cx = 50,
      cy = 50;
    const fit = () => {
      const bb = base.getBBox();
      const pad = 6;
      VB.x = bb.x - pad;
      VB.y = bb.y - pad;
      VB.w = bb.width + pad * 2;
      VB.h = bb.height + pad * 2;
      cx = VB.x + VB.w / 2;
      cy = VB.y + VB.h / 2;
      svg.setAttribute("viewBox", `${VB.x} ${VB.y} ${VB.w} ${VB.h}`);
    };
    fit();
    document.fonts?.ready.then(fit);
    window.addEventListener("resize", fit);

    const target = {
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      inside: false,
      lastMove: -1,
      t: -1,
    };
    const corePts = Array.from({ length: CORE }, () => ({ x: 0, y: 0 }));
    type P = {
      active: boolean;
      x: number;
      y: number;
      vx: number;
      vy: number;
      r0: number;
      age: number;
      life: number;
    };
    const drops: P[] = Array.from({ length: SPLASH }, () => ({
      active: false,
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      r0: 0,
      age: 0,
      life: 1,
    }));
    let reveal = 0,
      emitAcc = 0,
      lastT = performance.now() / 1000,
      raf = 0;
    const IDLE = 0.1;

    const move = (e: MouseEvent) => {
      const r = svg.getBoundingClientRect();
      const nx = VB.x + ((e.clientX - r.left) / r.width) * VB.w;
      const ny = VB.y + ((e.clientY - r.top) / r.height) * VB.h;
      const tnow = performance.now() / 1000;
      const dt = Math.max(1e-3, tnow - (target.t < 0 ? tnow : target.t));
      target.vx = (nx - target.x) / dt;
      target.vy = (ny - target.y) / dt;
      target.x = nx;
      target.y = ny;
      target.inside = true;
      target.lastMove = tnow;
      target.t = tnow;
    };
    const enter = () => {
      target.inside = true;
    };
    const leave = () => {
      target.inside = false;
    };
    title.addEventListener("mousemove", move);
    title.addEventListener("mouseenter", enter);
    title.addEventListener("mouseleave", leave);

    const spawn = () => {
      const p = drops.find((d) => !d.active);
      if (!p) return;
      p.active = true;
      p.age = 0;
      p.life = 0.85 + Math.random() * 0.7;
      p.x = target.x + (Math.random() - 0.5) * VB.h * 0.05;
      p.y = target.y + (Math.random() - 0.5) * VB.h * 0.05;
      const ang = Math.random() * TAU;
      const sp = VB.h * (0.05 + Math.random() * 0.16);
      p.vx = target.vx * 0.22 + Math.cos(ang) * sp;
      p.vy = target.vy * 0.22 + Math.sin(ang) * sp;
      p.r0 = VB.h * (0.045 + Math.random() * 0.075);
    };

    const loop = () => {
      const now = performance.now() / 1000;
      const dt = Math.min(0.05, Math.max(1e-3, now - lastT));
      lastT = now;
      const moving = target.inside && now - target.lastMove < IDLE;
      const want = moving ? 1 : 0;
      reveal += (want - reveal) * (want > reveal ? 0.32 : 0.045);
      if (reveal < 0.003) reveal = 0;

      // WARNA berganti + BALON kempes lalu mengembang (halus)
      const PH = PHASES.length;
      const PERIOD = 2.6;
      const tt = now / PERIOD;
      const idx = Math.floor(tt) % PH;
      const seg = tt - Math.floor(tt); // 0..1 dalam satu fase warna

      // Warna: stabil, lalu berganti tepat saat balon paling kempes
      let cf = 0;
      if (seg > 0.8) cf = 1;
      else if (seg > 0.7) {
        const u = (seg - 0.7) / 0.1;
        cf = u * u * (3 - 2 * u);
      }
      for (let k = 0; k < PH; k++) {
        const o = k === idx ? 1 - cf : k === (idx + 1) % PH ? cf : 0;
        phaseRefs.current[k]?.setAttribute("opacity", o.toFixed(3));
      }

      // Balon asli: mengembang → mengempes (kering, tanpa angin) → mengembang
      let bs = 1;
      if (seg >= 0.5) {
        const u = (seg - 0.5) / 0.5;
        if (u < 0.5) {
          const a = u / 0.5;
          bs = 1 - 0.72 * (a * a * (3 - 2 * a));
        } else {
          const a = (u - 0.5) / 0.5;
          const spring = 1 - Math.pow(1 - a, 2.2) * Math.cos(a * Math.PI * 1.4);
          bs = 0.28 + 0.72 * spring;
        }
      }
      const sx = 1 - (1 - bs) * 0.55;
      const sy = bs;
      scaleG.setAttribute(
        "transform",
        `translate(${cx} ${cy}) scale(${sx.toFixed(4)} ${sy.toFixed(4)}) translate(${-cx} ${-cy})`,
      );
      // Tekstur kerut: makin kempes makin berkerut (balon kering tanpa angin)
      dispRef.current?.setAttribute("scale", ((1 - bs) * 16).toFixed(2));

      // Pancarkan tetesan percikan sepanjang jejak kursor
      const speed = Math.hypot(target.vx, target.vy);
      if (moving) {
        emitAcc += speed * dt;
        const stepE = VB.h * 0.05;
        let guard = 0;
        while (emitAcc > stepE && guard < 6) {
          emitAcc -= stepE;
          spawn();
          guard++;
        }
      }

      // Badan cairan inti (menyatu, mengikuti kursor)
      const R = VB.h * reveal * 0.5;
      for (let i = 0; i < CORE; i++) {
        const s = i * 1.7;
        const ox = i === 0 ? 0 : Math.cos(now * 0.9 + s) * R * 0.16;
        const oy = i === 0 ? 0 : Math.sin(now * 1.1 + s) * R * 0.16;
        corePts[i].x +=
          (target.x + ox - corePts[i].x) * (i === 0 ? 0.45 : 0.32);
        corePts[i].y +=
          (target.y + oy - corePts[i].y) * (i === 0 ? 0.45 : 0.32);
        const rr =
          R * (i === 0 ? 0.4 : 0.26) * (1 + 0.06 * Math.sin(now * 2 + s));
        circ[i].setAttribute("cx", String(corePts[i].x));
        circ[i].setAttribute("cy", String(corePts[i].y));
        circ[i].setAttribute("r", String(Math.max(0, rr)));
      }

      // Tetesan percikan (splash)
      for (let j = 0; j < SPLASH; j++) {
        const p = drops[j];
        const c = circ[CORE + j];
        if (!p.active) {
          c.setAttribute("r", "0");
          continue;
        }
        p.age += dt;
        const lt = p.age / p.life;
        if (lt >= 1) {
          p.active = false;
          c.setAttribute("r", "0");
          continue;
        }
        p.vx *= 0.9;
        p.vy *= 0.9;
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        // Muncul cepat, lalu bertahan & memudar pelan (bekas percikan)
        const env =
          lt < 0.16 ? lt / 0.16 : Math.pow(1 - (lt - 0.16) / 0.84, 0.95);
        c.setAttribute("cx", String(p.x));
        c.setAttribute("cy", String(p.y));
        // Bentuk agak lancip: ditarik searah gerak → seperti percikan asli
        const spd = Math.hypot(p.vx, p.vy);
        const ang = (Math.atan2(p.vy, p.vx) * 180) / Math.PI;
        const stretch = 1 + Math.min(1.7, spd / (VB.h * 0.4));
        c.setAttribute("cx", "0");
        c.setAttribute("cy", "0");
        c.setAttribute("r", String(Math.max(0, p.r0 * env)));
        c.setAttribute(
          "transform",
          `translate(${p.x} ${p.y}) rotate(${ang.toFixed(1)}) scale(${stretch.toFixed(3)} ${(1 / Math.sqrt(stretch)).toFixed(3)})`,
        );
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", fit);
      title.removeEventListener("mousemove", move);
      title.removeEventListener("mouseenter", enter);
      title.removeEventListener("mouseleave", leave);
      circ.forEach((c) => c.remove());
    };
  }, []);

  const go = (e: React.MouseEvent, sel: string | number) => {
    e.preventDefault();
    setMenu(false);
    lenisRef.current?.scrollTo(sel as unknown as string, { offset: 0 });
  };

  return (
    <>
      <style>{CSS}</style>

      <div className="cursor-dot" ref={dotRef} />

      <div className={`loader ${loaded ? "done" : ""}`}>
        <span className="loader-brand">Cendekia™</span>
        <span className="loader-num" ref={loaderNum}>
          000
        </span>
        <span className="loader-cap">Kecerdasan Nusantara</span>
      </div>

      <span className="counter" ref={counter}>
        000
      </span>

      <nav className="nav">
        <a href="#top" className="logo" onClick={(e) => go(e, 0)}>
          Cendekia™
        </a>
        <div className="nav-r">
          <button className="menu-btn magnetic" onClick={() => setMenu(true)}>
            menu
          </button>
          <span className="lang">ID</span>
        </div>
      </nav>

      <div className={`menu-ov ${menu ? "open" : ""}`}>
        <button className="menu-close magnetic" onClick={() => setMenu(false)}>
          tutup ✕
        </button>
        <nav className="menu-links">
          <a href="#top" onClick={(e) => go(e, 0)}>
            <span>01</span>beranda
          </a>
          <a href="#asisten" onClick={(e) => go(e, "#asisten")}>
            <span>02</span>asisten
          </a>
          <a href="#fitur" onClick={(e) => go(e, "#fitur")}>
            <span>03</span>fitur
          </a>
          <a href="/">
            <span>04</span>masuk aplikasi ↗
          </a>
        </nav>
        <div className="menu-foot">
          <span>Kecerdasan Nusantara</span>
          <span>© 2026</span>
        </div>
      </div>

      <main>
        <section className="hero" id="top">
          <div className="hero-top">
            <div className="hero-tag">
              <span className="pill">✦ Kecerdasan Nusantara</span>
              <p className="hero-mini">
                Bukan sekadar menjawab, tapi memahami.
                <br />
                Karena pemahaman adalah segalanya.
              </p>
            </div>
            <span className="hero-mini right">
              Studio AI — Nusantara
              <br />© 26
            </span>
          </div>

          <div className="hero-title" ref={heroTitleRef}>
            <svg
              className="hero-svg"
              ref={heroSvgRef}
              xmlns="http://www.w3.org/2000/svg"
              aria-label="CENDEKIA"
            >
              <defs>
                {/* Lima gradien metalik — nada asli noth.in */}
                <linearGradient id="gRed" x1="0" y1="0" x2="0.12" y2="1">
                  <stop offset="0" stopColor="#f6e2e3" />
                  <stop offset="0.3" stopColor="#a8424a" />
                  <stop offset="0.55" stopColor="#592026" />
                  <stop offset="0.8" stopColor="#8e2e35" />
                  <stop offset="1" stopColor="#3a0f13" />
                </linearGradient>
                <linearGradient id="gRose" x1="0" y1="0" x2="0.12" y2="1">
                  <stop offset="0" stopColor="#ffeef0" />
                  <stop offset="0.3" stopColor="#d38d91" />
                  <stop offset="0.55" stopColor="#cb6f73" />
                  <stop offset="0.8" stopColor="#a8555a" />
                  <stop offset="1" stopColor="#6e2b30" />
                </linearGradient>
                <linearGradient id="gTeal" x1="0" y1="0" x2="0.12" y2="1">
                  <stop offset="0" stopColor="#eaf3f0" />
                  <stop offset="0.3" stopColor="#6f9a92" />
                  <stop offset="0.55" stopColor="#2b4e49" />
                  <stop offset="0.8" stopColor="#304d46" />
                  <stop offset="1" stopColor="#16302b" />
                </linearGradient>
                <linearGradient id="gBronze" x1="0" y1="0" x2="0.12" y2="1">
                  <stop offset="0" stopColor="#f6ecdf" />
                  <stop offset="0.3" stopColor="#b98f6e" />
                  <stop offset="0.55" stopColor="#8d6954" />
                  <stop offset="0.8" stopColor="#6e4f3d" />
                  <stop offset="1" stopColor="#3c2a20" />
                </linearGradient>
                <linearGradient id="gTaupe" x1="0" y1="0" x2="0.12" y2="1">
                  <stop offset="0" stopColor="#f4efe9" />
                  <stop offset="0.3" stopColor="#b3a596" />
                  <stop offset="0.55" stopColor="#8c796b" />
                  <stop offset="0.8" stopColor="#6d5d51" />
                  <stop offset="1" stopColor="#3f342d" />
                </linearGradient>
                {/* Gumpalan gooey (blur 6 — percikan kecil & halus) */}
                <filter id="hgoo">
                  <feGaussianBlur
                    in="SourceGraphic"
                    stdDeviation="4.5"
                    result="b"
                  />
                  <feColorMatrix
                    in="b"
                    mode="matrix"
                    values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 24 -11"
                  />
                </filter>
                {/* Balon asli: kerut (displacement) + bevel empuk + gloss + tekstur */}
                <filter
                  id="hballoon"
                  x="-45%"
                  y="-45%"
                  width="190%"
                  height="190%"
                >
                  <feTurbulence
                    type="fractalNoise"
                    baseFrequency="0.04 0.07"
                    numOctaves="2"
                    seed="4"
                    result="turb"
                  />
                  <feDisplacementMap
                    ref={dispRef}
                    in="SourceGraphic"
                    in2="turb"
                    scale="0"
                    xChannelSelector="R"
                    yChannelSelector="G"
                    result="disp"
                  />
                  <feGaussianBlur in="disp" stdDeviation="3.2" result="bl" />
                  <feSpecularLighting
                    in="bl"
                    surfaceScale="5"
                    specularConstant="0.85"
                    specularExponent="20"
                    lightingColor="#ffffff"
                    result="sp"
                  >
                    <fePointLight x="-40" y="-80" z="130" />
                  </feSpecularLighting>
                  <feComposite in="sp" in2="disp" operator="in" result="spC" />
                  <feTurbulence
                    type="fractalNoise"
                    baseFrequency="0.9"
                    numOctaves="2"
                    seed="7"
                    result="noise"
                  />
                  <feColorMatrix
                    in="noise"
                    type="matrix"
                    values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.22 0"
                    result="grain"
                  />
                  <feComposite
                    in="grain"
                    in2="disp"
                    operator="in"
                    result="grainClip"
                  />
                  <feMerge>
                    <feMergeNode in="disp" />
                    <feMergeNode in="grainClip" />
                    <feMergeNode in="spC" />
                  </feMerge>
                </filter>
                <mask id="hblob">
                  <rect
                    x="-9999"
                    y="-9999"
                    width="99999"
                    height="99999"
                    fill="black"
                  />
                  <g filter="url(#hgoo)" ref={blobRef} />
                </mask>
              </defs>

              {/* LAYER DEPAN: teks hitam di atas background putih */}
              <text ref={baseRef} className="hs" x="0" y="100" fill="#0d0d0d">
                CENDEKIA
              </text>

              {/* LAYER BELAKANG: balon bertekstur, warna berganti + kempes/mengembang */}
              <g mask="url(#hblob)">
                <rect
                  x="-9999"
                  y="-9999"
                  width="99999"
                  height="99999"
                  fill="#0d0d0d"
                />
                <g ref={scaleGroupRef}>
                  {PHASES.map((g, k) => (
                    <g
                      key={k}
                      ref={(el) => {
                        phaseRefs.current[k] = el;
                      }}
                      opacity="0"
                    >
                      <text
                        className="hs hs-balloon"
                        x="0"
                        y="100"
                        fill={`url(#${g})`}
                        filter="url(#hballoon)"
                      >
                        CENDEKIA
                      </text>
                    </g>
                  ))}
                </g>
              </g>
            </svg>
          </div>

          <div className="hero-foot">
            <span className="hero-mini">( gulir untuk menjelajah )</span>
            <span className="hero-mini">ID / EN</span>
          </div>
        </section>

        <section className="blok">
          <span className="seksi-label">01 — Manifesto</span>
          <Judul
            className="besar"
            text={
              "Kebanyakan AI menghasilkan jawaban.\nKami memilih pemahaman."
            }
          />
          <Reveal delay={200}>
            <p className="paragraf">
              Di dunia yang dibanjiri informasi, yang langka adalah kejernihan.
              Cendekia membaca dokumenmu, menautkan tiap klaim ke sumbernya, dan
              menjawab dengan tenang — berakar pada semangat Nusantara.
            </p>
          </Reveal>
        </section>

        <RobotStage />

        <section className="blok tengah">
          <Judul
            className="besar"
            text={"AI baik menjawab.\nAI hebat membuatmu mengerti."}
          />
        </section>

        <GaleriPinned />

        <div className="marquee">
          <div className="marquee-inner">
            {Array.from({ length: 6 }).map((_, i) => (
              <span key={i}>CENDEKIA — KECERDASAN NUSANTARA — </span>
            ))}
          </div>
        </div>

        <section className="cta">
          <span className="seksi-label">04 — Mulai</span>
          <Judul
            className="raksasa kecil"
            text={"Mulai dari\nsebuah pertanyaan."}
          />
          <Reveal delay={200}>
            <a href="/" className="tombol besar-tombol magnetic">
              masuk aplikasi ↗
            </a>
          </Reveal>
        </section>

        <footer className="footer">
          <div className="footer-cols">
            <div className="footer-col">
              <span className="seksi-label light">Terhubung</span>
              <a
                href="https://github.com/michaelalinskie11"
                target="_blank"
                rel="noreferrer"
              >
                GitHub ↗
              </a>
              <a href="/">Aplikasi ↗</a>
              <a href="mailto:michaelalinskie11@gmail.com">Email ↗</a>
            </div>
            <div className="footer-col right">
              <span>Cendekia · Kecerdasan Nusantara</span>
              <span>Dirancang oleh Michael Alinskie · 2026</span>
            </div>
          </div>
          <div className="footer-big">CENDEKIA</div>
        </footer>
      </main>
    </>
  );
}

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=Archivo+Black&family=Baloo+2:wght@800&display=swap');
.hs.hs-balloon{font-family:'Baloo 2','Archivo Black',sans-serif;font-weight:800;letter-spacing:-1px;}
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-stopped { overflow: hidden; }

:root{ --bg:#ffffff; --ink:#0c0c0c; --muted:#8a8983; --line:rgba(12,12,12,0.14); }
html,body{background:var(--bg);}
body{font-family:'Archivo',system-ui,sans-serif;color:var(--ink);cursor:none;}
main{position:relative;z-index:3;overflow-x:hidden;}

.cursor-dot{position:fixed;top:0;left:0;width:6px;height:6px;border-radius:50%;background:#ffffff;mix-blend-mode:difference;pointer-events:none;z-index:9999;will-change:transform;}

.loader{position:fixed;inset:0;z-index:80;background:var(--bg);display:flex;flex-direction:column;justify-content:center;align-items:center;gap:8px;transition:transform 1s cubic-bezier(.76,0,.24,1);}
.loader.done{transform:translateY(-100%);}
.loader-brand{font-size:13px;letter-spacing:.02em;}
.loader-num{font-family:'Archivo Black',sans-serif;font-size:clamp(90px,18vw,260px);line-height:.9;letter-spacing:-.03em;}
.loader-cap{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);}

.counter{position:fixed;bottom:22px;right:30px;z-index:45;font-size:12px;letter-spacing:.2em;color:#fff;mix-blend-mode:difference;}

.nav{position:fixed;top:0;left:0;width:100%;z-index:30;display:flex;justify-content:space-between;align-items:center;padding:22px 34px;color:#fff;mix-blend-mode:difference;}
.logo{font-weight:700;font-size:17px;letter-spacing:-.01em;color:inherit;text-decoration:none;}
.nav-r{display:flex;gap:20px;align-items:center;}
.menu-btn{background:none;border:none;font-family:inherit;font-size:14px;color:inherit;padding:0;cursor:pointer;}
.lang{font-size:12px;letter-spacing:.12em;opacity:.7;}

.menu-ov{position:fixed;inset:0;z-index:40;background:#0a0a0a;color:var(--bg);transform:translateY(-100%);transition:transform .8s cubic-bezier(.76,0,.24,1);display:flex;flex-direction:column;justify-content:center;padding:0 34px;}
.menu-ov.open{transform:translateY(0);}
.menu-close{position:absolute;top:22px;right:34px;background:none;border:none;font-family:inherit;font-size:14px;color:var(--bg);cursor:pointer;}
.menu-links{display:flex;flex-direction:column;gap:2px;}
.menu-links a{display:flex;align-items:baseline;gap:20px;text-decoration:none;color:var(--bg);font-family:'Archivo Black',sans-serif;font-size:clamp(42px,10vw,120px);line-height:1.02;letter-spacing:-.03em;opacity:.5;transition:opacity .3s ease,padding-left .3s ease;}
.menu-links a:hover{opacity:1;padding-left:14px;}
.menu-links a span{font-family:'Archivo';font-size:14px;font-weight:500;opacity:.5;letter-spacing:0;}
.menu-foot{position:absolute;bottom:28px;left:34px;right:34px;display:flex;justify-content:space-between;font-size:13px;color:rgba(244,243,240,.6);}

section{padding:0 34px;}
.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center;position:relative;}
.hero-top{position:absolute;top:104px;left:34px;right:34px;display:flex;justify-content:space-between;align-items:flex-start;gap:20px;z-index:3;}
.hero-tag{display:flex;flex-direction:column;gap:14px;}
.pill{align-self:flex-start;background:var(--ink);color:var(--bg);font-size:12px;letter-spacing:.02em;padding:8px 15px;border-radius:999px;}
.hero-mini{font-size:13px;line-height:1.4;color:var(--ink);opacity:.75;}
.hero-mini.right{text-align:right;}
.raksasa{font-family:'Arial Black','Archivo Black',Impact,sans-serif;font-weight:900;line-height:.82;letter-spacing:-.045em;font-size:clamp(64px,20vw,340px);margin:0;white-space:nowrap;}
.raksasa.kecil{font-size:clamp(46px,12vw,180px);white-space:normal;letter-spacing:-.03em;}
.hero-foot{position:absolute;bottom:30px;left:34px;right:34px;display:flex;justify-content:space-between;text-transform:uppercase;letter-spacing:.08em;z-index:3;}
.hero-title{position:relative;width:100%;display:flex;justify-content:center;align-items:center;z-index:2;padding:0 2vw;}
.hero-svg{width:96%;height:auto;overflow:visible;display:block;}
.hs{font-family:'Arial Black','Archivo Black',Impact,sans-serif;font-weight:900;font-size:100px;letter-spacing:-4.5px;}

.blok{padding-top:22vh;padding-bottom:8vh;max-width:1200px;margin:0 auto;}
.blok.tengah{padding-top:16vh;text-align:right;}
.seksi-label{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:26px;}
.seksi-label.light{color:rgba(244,243,240,.7);}
.besar{font-family:'Archivo Black',sans-serif;font-weight:400;font-size:clamp(30px,5.4vw,74px);line-height:1.0;letter-spacing:-.025em;}
.paragraf{margin-top:26px;max-width:52ch;font-size:clamp(16px,1.5vw,20px);line-height:1.6;color:#33322e;}

.robot-stage{position:relative;height:180vh;background:radial-gradient(120% 90% at 50% 12%,#16161d 0%,#0b0b0e 52%,#070708 100%);}
.robot-sticky{position:sticky;top:0;height:100vh;overflow:hidden;display:flex;align-items:center;justify-content:center;}
.robot-glow{position:absolute;left:50%;top:55%;width:min(96vw,900px);height:min(96vw,900px);transform:translate(-50%,-50%);background:radial-gradient(circle,rgba(96,116,214,.30) 0%,rgba(214,116,166,.12) 42%,rgba(10,10,10,0) 66%);filter:blur(24px);pointer-events:none;z-index:0;}
.robot-canvas{position:absolute;inset:0;z-index:1;pointer-events:auto;}
.robot-canvas .spline-robot{width:100%;height:100%;}
.robot-canvas canvas{display:block;width:100%!important;height:100%!important;}
.robot-copy{position:absolute;top:104px;left:48px;right:48px;z-index:2;pointer-events:none;max-width:600px;}
.robot-h{font-family:'Archivo Black',sans-serif;font-weight:400;color:#f4f3f0;font-size:clamp(32px,5.4vw,74px);line-height:1.02;letter-spacing:-.03em;margin:18px 0 0;max-width:13ch;}
.robot-sub{color:rgba(244,243,240,.64);margin-top:18px;font-size:clamp(14px,1.4vw,17px);line-height:1.65;max-width:34ch;}
.robot-cta{display:inline-flex;align-items:center;gap:9px;margin-top:26px;padding:13px 24px;border-radius:999px;background:#f4f3f0;color:#0b0b0e;font-family:'Archivo',sans-serif;font-weight:600;font-size:14px;letter-spacing:.01em;text-decoration:none;pointer-events:auto;transition:transform .25s ease,box-shadow .25s ease;box-shadow:0 8px 30px rgba(142,162,255,.18);}
.robot-cta span{transition:transform .25s ease;}
.robot-cta:hover{transform:translateY(-2px);box-shadow:0 14px 40px rgba(142,162,255,.34);}
.robot-cta:hover span{transform:translateX(4px);}
.robot-hint{position:absolute;bottom:40px;left:50%;transform:translateX(-50%);display:inline-flex;align-items:center;gap:8px;padding:9px 18px;border:1px solid rgba(244,243,240,.16);border-radius:999px;background:rgba(244,243,240,.04);backdrop-filter:blur(6px);color:rgba(244,243,240,.62);font-size:11px;letter-spacing:.16em;text-transform:uppercase;white-space:nowrap;z-index:2;pointer-events:none;animation:hintPulse 2.8s ease-in-out infinite;}
.robot-hint::before{content:"";width:6px;height:6px;border-radius:50%;background:#8ea2ff;box-shadow:0 0 8px #8ea2ff;}
@keyframes hintPulse{0%,100%{opacity:.55;}50%{opacity:1;}}
.spline-load{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:rgba(244,243,240,.5);font-size:12px;letter-spacing:.12em;text-transform:uppercase;}

.pin{height:360vh;position:relative;}
.pin-sticky{position:sticky;top:0;height:100vh;display:flex;align-items:center;overflow:hidden;}
.track{display:flex;align-items:center;padding:0 34px;will-change:transform;}
.kartu{position:relative;flex:0 0 auto;width:min(72vw,430px);height:56vh;margin-right:30px;border-radius:18px;border:1px solid var(--line);background:#fff;overflow:hidden;padding:36px;display:flex;flex-direction:column;justify-content:flex-end;}
.kartu-no{font-size:12px;color:var(--muted);letter-spacing:.12em;}
.kartu-judul{font-family:'Archivo Black',sans-serif;font-weight:400;font-size:clamp(26px,3.4vw,42px);letter-spacing:-.02em;margin:8px 0 12px;}
.kartu-teks{font-size:clamp(14px,1.4vw,18px);color:#33322e;margin:0;max-width:26ch;}
.kartu-intro{background:transparent;border:none;justify-content:center;width:min(84vw,520px);}
.kartu-intro-h{font-family:'Archivo Black',sans-serif;font-weight:400;font-size:clamp(34px,5vw,68px);line-height:.98;letter-spacing:-.02em;margin:12px 0 0;}

.marquee{overflow:hidden;white-space:nowrap;padding:46px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:12vh;}
.marquee-inner{display:inline-block;animation:slide 28s linear infinite;}
.marquee-inner span{font-family:'Archivo Black',sans-serif;font-size:clamp(30px,6vw,84px);letter-spacing:-.02em;}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}

.cta{min-height:80vh;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;max-width:1200px;margin:0 auto;}
.tombol{display:inline-block;background:var(--ink);color:var(--bg);text-decoration:none;font-size:15px;padding:13px 28px;border-radius:999px;transition:transform .3s cubic-bezier(.2,.7,.2,1);}
.besar-tombol{font-size:17px;padding:17px 38px;margin-top:32px;}
.magnetic{transition:transform .3s cubic-bezier(.2,.7,.2,1);will-change:transform;}

.footer{background:#0a0a0a;color:var(--bg);padding:70px 34px 40px;margin-top:10vh;}
.footer-cols{display:flex;justify-content:space-between;flex-wrap:wrap;gap:24px;border-bottom:1px solid rgba(244,243,240,.16);padding-bottom:40px;}
.footer-col{display:flex;flex-direction:column;gap:8px;}
.footer-col a{color:var(--bg);text-decoration:none;font-size:17px;opacity:.85;}
.footer-col a:hover{opacity:1;}
.footer-col.right{text-align:right;font-size:13px;color:rgba(244,243,240,.6);gap:6px;}
.footer-big{font-family:'Archivo Black',sans-serif;font-weight:400;font-size:clamp(70px,21vw,340px);line-height:.9;letter-spacing:-.04em;margin-top:20px;white-space:nowrap;}

.reveal{opacity:0;transform:translateY(30px);transition:opacity 1s cubic-bezier(.2,.7,.2,1),transform 1s cubic-bezier(.2,.7,.2,1);}
.reveal.in{opacity:1;transform:none;}
.mask-line{display:block;}
.mask{display:inline-block;overflow:hidden;vertical-align:top;}
.word{display:inline-block;margin-right:.26em;transform:translateY(115%);transition:transform .9s cubic-bezier(.16,.84,.3,1);}
.mask-wrap.in .word{transform:translateY(0);}

@media(max-width:720px){
  body{cursor:auto;}
  .cursor-dot{display:none;}
  .nav,section,.footer{padding-left:18px;padding-right:18px;}
  .hero-top{left:18px;right:18px;}
  .hero-foot{left:18px;right:18px;}
  .robot-stage{height:150vh;}
  .robot-copy{top:92px;left:18px;right:18px;}
  .robot-glow{top:58%;}
  .track{padding:0 18px;}
  .kartu{width:82vw;height:54vh;}
  .menu-ov{padding:0 18px;}
  .menu-close{right:18px;}
  .menu-foot{left:18px;right:18px;}
  .blok.tengah{text-align:left;}
  .raksasa{white-space:normal;}
}
`;
