# Tinjauan Proyek & Analisis Kesenjangan
**Tanggal:** 2026-02-04
**Lingkup:** Tinjauan `sistem-pa` terhadap `PROJECT_CHARTER.md`

## 1. Ringkasan Eksekutif
Proyek ini memiliki fondasi yang kuat dengan aplikasi Flask yang berfungsi, database SQLite, dan kontrol akses berbasis peran (RBAC) dasar. Skema database inti mencakup semua persyaratan (8+ tabel), dan fitur-fitur utama seperti "Obrolan Real-time" dan "Ekspor Dokumen" (PDF, Word, Excel) sudah diimplementasikan.

Namun, terdapat **Kerentanan Keamanan Kritis** terkait penyimpanan kata sandi yang harus segera ditangani sebelum penerapan (deployment). Selain itu, arsitektur "Blueprint per peran" saat ini diimplementasikan sebagai monolit "Blueprint per fitur", yang dapat memengaruhi pemeliharaan saat proyek berkembang.

## 2. Audit Keamanan (KRITIS)
| Tingkat | Temuan | Deskripsi | Rekomendasi |
| :--- | :--- | :--- | :--- |
| **KRITIS** | **Password Teks Biasa** | Kata sandi pengguna disimpan langsung di tabel `users` tanpa di-hash (misalnya, `admin123`). Ini memungkinkan siapa saja dengan akses DB untuk membaca semua kredensial. | **Perbaikan Segera:** Implementasikan `werkzeug.security.generate_password_hash` dan `check_password_hash`. |
| **Tinggi** | **Implementasi 2FA** | "2FA" saat ini adalah PIN 6 digit statis yang disimpan di DB. Meskipun menambah lapisan keamanan, ini bukan solusi TOTP (Time-based One-Time Password) standar. | **Tingkatkan:** Pertimbangkan mengintegrasikan pustaka TOTP yang tepat (seperti `pyotp`) untuk 2FA dinamis yang sebenarnya, atau ubah nama fitur menjadi "Verifikasi PIN 2 Langkah". |
| **Sedang** | **Rahasia di Hardcode** | Kode program mungkin berisi logika spesifik yang di-hardcode untuk "admin_it" yang seharusnya lebih berbasis kebijakan. | Pindahkan definisi kebijakan peran ke konfigurasi atau tegakkan kontrol akses berbasis dekorator secara ketat. |

## 3. Arsitektur & Struktur Kode
*   **Blueprints**: Piagam (charter) meminta "API Flask modular (blueprint per peran)". Saat ini, `dashboard.py` adalah kontroler monolitik yang menangani logika untuk *semua* peran (`input_perkara`, `update_hakim`, `update_panitera`).
    *   **Rekomendasi**: Pecah `dashboard.py` menjadi `dashboard_staff.py`, `dashboard_hakim.py`, `dashboard_panitera.py` agar lebih selaras dengan piagam dan meningkatkan isolasi kode.
*   **Database**: Skema di `db.py` sangat baik dan sesuai dengan persyaratan dengan sempurna.
*   **Websockets**: `ws.py` mengimplementasikan obrolan real-time dengan benar menggunakan `flask-sock`, yang merupakan pilihan yang tangguh.

## 4. Analisis Kesenjangan Fitur

| Fitur | Persyaratan Piagam | Implementasi Saat Ini | Status |
| :--- | :--- | :--- | :--- |
| **Dashboard** | Verifikasi berbasis peran | Diimplementasikan melalui pemeriksaan `if session['role']...`. | ✅ Berfungsi |
| **Otomasi Dokumen** | "Otomasi dokumen... akta cerai" | Ekspor PDF/Word ada (`export.py`). | ✅ Berfungsi |
| **Tanda Tangan Digital** | "QR code/barcode" | Menggunakan gambar barcode **statis** dari pengaturan. **Tidak** menghasilkan kode QR unik per dokumen. | ⚠️ Parsial |
| **Web Publik** | "Website publik... jadwal sidang" | Blueprint `public.py` ada. | ✅ Berfungsi |
| **Chat** | "Real-time chat internal" | Implementasi Websocket di `ws.py`. | ✅ Berfungsi |

## 5. Peta Jalan yang Direkomendasikan
1.  **Fase 0: Pengerasan Keamanan** (Hari 1)
    *   Migrasikan semua kata sandi ke versi hash.
    *   Amankan manajemen sesi.
2.  **Fase 1: Refaktor Arsitektur** (Hari 2-3)
    *   Pecah `dashboard.py` menjadi blueprint spesifik peran.
    *   Standarisasi respons API (HTMX/JSON).
3.  **Fase 2: Penyelesaian Fitur** (Hari 4)
    *   Implementasikan **Pembuatan Kode QR Dinamis** (misalnya, menggunakan pustaka `qrcode`) yang menyematkan URL verifikasi.
    *   Verifikasi konten "Situs Web Publik" sesuai dengan data yang di-seed.

---
**Kesimpulan**: Proyek ini sekitar 75% selesai berdasarkan piagam. Penghambat terbesar adalah keamanan. Setelah diperbaiki, sistem secara fungsional sangat dekat dengan tujuan.