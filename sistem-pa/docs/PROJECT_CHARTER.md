# Project Charter: Sistem Informasi Pengadilan Agama IKN

## Tujuan Proyek (Project Purpose)

Mengembangkan sistem informasi terintegrasi untuk mendukung manajemen perkara perceraian di Pengadilan Agama Ibukota Nusantara (PA IKN), dengan fokus pada:
- **Digitalisasi Proses**: Menggantikan pencatatan manual dengan sistem digital terpusat.
- **Transparansi Publik**: Menyediakan akses informasi jadwal sidang dan profil pegawai tanpa login.
- **Keamanan Data**: Autentikasi berlapis (username, PIN, CAPTCHA) untuk melindungi data sensitif.

---

## Objektif (Objectives)

| Objektif | Target |
|---|---|
| Kecepatan Proses | Pendaftaran perkara dapat diselesaikan dalam hitungan menit |
| Akurasi Data | Validasi form untuk meminimalkan kesalahan input |
| Transparansi | Website publik aktif 24/7 dengan data terkini |
| Kemudahan Akses | Dashboard berbasis web, dapat diakses dari browser standar |

---

## Fase Implementasi

### Phase 1: Backend & Database ✅
- API Flask modular dengan blueprint: `auth`, `public`, `dashboard`, `admin`, `export`, `uploads`.
- SQLite schema dengan tabel utama: `users`, `perkara`, `diskusi`, `laporan_tamu`, `berita`, `galeri`, `pengaturan`, `mediasi`, `akta_cerai`.
- Autentikasi: Username + PIN 6-digit + CAPTCHA (operasi matematika).
- Soft Delete & Audit Columns (`is_deleted`, `created_at`, `updated_at`, dll.) pada semua tabel utama.
- UUID sebagai primary key untuk semua entitas.

### Phase 2: Frontend & UI ✅
- Dashboard responsif dengan akses berbasis role (`admin_it`, `ketua`, `hakim`, `panitera`, `staff`).
- Antarmuka HTMX untuk interaksi tanpa reload halaman.
- Bootstrap 5 untuk styling dan komponen UI.
- Form input perkara dengan validasi client-side dan server-side.

### Phase 3: Fitur Terintegrasi ✅
- Real-time chat internal via WebSocket (`/chatroom`).
- Website publik: Landing Page, Jadwal Sidang, Profil Pegawai, Sejarah, Visi-Misi.
- CMS untuk admin: upload logo, background, berita, galeri.
- Export data ke PDF, Word, dan Excel.

### Phase 4: Dokumentasi ✅
- Swagger UI (`/docs`) dan JSON Spec (`/spec`) untuk dokumentasi API.
- Dokumentasi teknis (`TECHNICAL.md`, `API.md`).

---

## Lingkup (Scope)

### DALAM LINGKUP (In Scope):
- Manajemen perkara perceraian (cerai talak, cerai gugat).
- Modul autentikasi 3-langkah (username, PIN, CAPTCHA).
- Chat internal antar pegawai.
- Website publik (jadwal sidang, profil pegawai).
- Export data (Excel, PDF, Word).
- CMS untuk konten publik (berita, galeri).
- Dokumentasi API (Swagger).

### DI LUAR LINGKUP (Out of Scope):
- Integrasi dengan sistem eksternal (SIPP Mahkamah Agung, e-Filing).
- Aplikasi mobile native (sistem hanya berbasis web responsif).
- Multi-bahasa (hanya Bahasa Indonesia).
- Jenis perkara non-perceraian (itsbat nikah, waris, wakaf, dll.).
- Notifikasi SMS/Email.
- Deployment server produksi (Docker/Ubuntu) - disediakan terpisah.