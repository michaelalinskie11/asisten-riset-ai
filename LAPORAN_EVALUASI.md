# Laporan Evaluasi RAG — Cendekia

Evaluasi otomatis atas sistem Retrieval-Augmented Generation.

## Ringkasan Skor

| Metrik | Skor |
|---|---|
| Retrieval Hit Rate | 100.0% (6/6) |
| Answer Accuracy | 100.0% (6/6) |
| Penolakan benar (anti-halusinasi) | 100.0% (1/1) |
| Rata-rata Faithfulness | 5.00/5 |
| Rata-rata Relevance | 4.43/5 |

## Rincian per Pertanyaan

| Pertanyaan | Jawaban | Retrieval | Faith | Rel | Status |
|---|---|:--:|:--:|:--:|:--:|
| Kapan dan di mana NusantaraByte didirikan? | NusantaraByte didirikan pada tahun 2023 di kota Surabaya, Indonesia. | ✓ | 5 | 5 | ✅ |
| Siapa CEO NusantaraByte? | CEO NusantaraByte adalah Michael Alinskie. | ✓ | 5 | 5 | ✅ |
| Apa nama produk utama NusantaraByte? | Nama produk utama NusantaraByte adalah Lontara AI. | ✓ | 5 | 5 | ✅ |
| Berapa harga paket Profesional? | Harga paket Profesional adalah Rp450.000 per bulan. | ✓ | 5 | 5 | ✅ |
| Fitur bahasa daerah apa yang direncanakan pada Q4 2026? | Bahasa daerah yang direncanakan untuk mendukung pada Q4 2026 adalah bahasa Jawa dan bahasa... | ✓ | 5 | 5 | ✅ |
| Berapa target pengguna aktif bulanan (MAU) di akhir 2026? | Target jumlah pengguna aktif bulanan pada akhir 2026 adalah 30.000 pengguna. | ✓ | 5 | 5 | ✅ |
| Siapa pelatih tim nasional sepak bola Argentina? | Tidak ada di dokumen. | - | 5 | 1 | ✅ |

*Faithfulness & Relevance dinilai oleh LLM-as-judge (llama-3.3-70b-versatile).*
