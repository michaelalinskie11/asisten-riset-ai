"""
Fase 3 — PostgreSQL: menyimpan dokumen & riwayat chat secara permanen
=====================================================================
Sampai sekarang, semua data hilang saat aplikasi ditutup (hanya di memori).
Database membuat data BERTAHAN — fondasi setiap produk nyata.

Kita pakai PostgreSQL di cloud lewat Supabase (gratis). Modul ini:
  • init_db()          -> membuat tabel bila belum ada
  • simpan_dokumen()   -> catat dokumen yang diunggah
  • simpan_riwayat()   -> catat setiap tanya-jawab
  • ambil_riwayat()    -> baca kembali riwayat terakhir

Butuh:  pip install psycopg2-binary
        .env berisi DATABASE_URL (connection string dari Supabase)

Jalankan:  python basis_data.py
"""

import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def _koneksi():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL belum diatur di .env")
    return psycopg2.connect(DATABASE_URL)


# ============================================================
# Membuat tabel (jalankan sekali; aman diulang)
# ============================================================
def init_db():
    with _koneksi() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dokumen (
                id              SERIAL PRIMARY KEY,
                nama            TEXT NOT NULL,
                jumlah_potongan INTEGER DEFAULT 0,
                dibuat          TIMESTAMPTZ DEFAULT now()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS riwayat (
                id         SERIAL PRIMARY KEY,
                pertanyaan TEXT NOT NULL,
                jawaban    TEXT NOT NULL,
                dibuat     TIMESTAMPTZ DEFAULT now()
            );
        """)
        conn.commit()
    print("✅ Tabel 'dokumen' & 'riwayat' siap.")


# ============================================================
# Operasi tulis
# ============================================================
def simpan_dokumen(nama, jumlah_potongan=0):
    with _koneksi() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO dokumen (nama, jumlah_potongan) VALUES (%s, %s) RETURNING id;",
            (nama, jumlah_potongan),
        )
        id_baru = cur.fetchone()[0]
        conn.commit()
    print(f"📄 Dokumen tersimpan (id={id_baru}): {nama}")
    return id_baru


def simpan_riwayat(pertanyaan, jawaban):
    with _koneksi() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO riwayat (pertanyaan, jawaban) VALUES (%s, %s) RETURNING id;",
            (pertanyaan, jawaban),
        )
        id_baru = cur.fetchone()[0]
        conn.commit()
    return id_baru


# ============================================================
# Operasi baca
# ============================================================
def ambil_riwayat(limit=10):
    with _koneksi() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, pertanyaan, jawaban, dibuat FROM riwayat ORDER BY dibuat DESC LIMIT %s;",
            (limit,),
        )
        return cur.fetchall()


def ambil_dokumen(limit=10):
    with _koneksi() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, nama, jumlah_potongan, dibuat FROM dokumen ORDER BY dibuat DESC LIMIT %s;",
            (limit,),
        )
        return cur.fetchall()


def main():
    print("=" * 60)
    print("  POSTGRESQL — Cendekia (Fase 3)")
    print("=" * 60)

    if not DATABASE_URL:
        print("❌ DATABASE_URL belum diatur di .env (lihat panduan Supabase).")
        return

    # 1) Siapkan tabel
    init_db()

    # 2) Coba simpan contoh data
    print("\n▶️  Menyimpan contoh data...")
    simpan_dokumen("dokumen.pdf", jumlah_potongan=6)
    simpan_riwayat("Siapa CEO NusantaraByte?", "CEO-nya adalah Michael Alinskie.")

    # 3) Baca kembali
    print("\n📚 Riwayat terakhir:")
    for r in ambil_riwayat(5):
        print(f"   [{r['dibuat']:%Y-%m-%d %H:%M}] Q: {r['pertanyaan']}")
        print(f"       A: {r['jawaban']}")

    print("\n📄 Dokumen tercatat:")
    for d in ambil_dokumen(5):
        print(f"   • {d['nama']} ({d['jumlah_potongan']} potongan) — {d['dibuat']:%Y-%m-%d %H:%M}")

    print("\n🎉 Database bekerja! Data ini akan tetap ada meski aplikasi ditutup.")


if __name__ == "__main__":
    main()
