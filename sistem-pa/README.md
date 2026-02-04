# Sistem Informasi Pengadilan Agama Ibukota Nusantara (Sistem-PA IKN)

Sistem informasi terintegrasi untuk mendukung manajemen perkara perceraian di Pengadilan Agama Ibukota Nusantara, dengan fokus pada otomasi proses, keamanan berlapis, dan transparansi pelayanan publik.

## 🚀 Fitur Utama

*   **Manajemen Perkara**: Pendaftaran dan pelacakan perkara peceraian (Cerai Talak & Cerai Gugat).
*   **Otomasi Dokumen**: Penerbitan Akta Cerai otomatis dengan tanda tangan digital (Barcode/QR).
*   **Keamanan Berlapis**: Autentikasi menggunakan password dan verifikasi PIN 6-digit.
*   **Dashboard Multi-Role**: Akses khusus untuk Admin IT, Ketua, Hakim, Panitera, Staff, dan Publik.
*   **Real-time Chat**: Komunikasi internal antar pegawai menggunakan Flask-Sock (Websockets).
*   **Portal Publik**: Jadwal sidang real-time dan profil pegawai yang dapat diakses masyarakat tanpa login.
*   **Ekspor Data**: Mendukung ekspor ke format PDF, Docx (Word), dan XLSX (Excel).

## 🛠️ Tech Stack

*   **Backend**: Python, Flask
*   **Database**: SQLite
*   **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, HTMX
*   **Real-time**: Flask-Sock (Websockets)
*   **Containerization**: Docker & Docker Compose

## 📦 Instalasi & Menjalankan Lokal

1. **Clone Repository**
   ```bash
   git clone https://github.com/heryandp/tugas_unsia.git
   cd tugas_unsia/sistem-pa
   ```

2. **Buat Virtual Environment (Opsional tapi disarankan)**
   ```bash
   python -m venv env
   source env/bin/scripts/activate  # Untuk Windows: env\Scripts\activate
   ```

3. **Install Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Aplikasi**
   ```bash
   python app.py
   ```
   Buka `http://127.0.0.1:5000` di browser Anda.

## 🔐 Kredensial Default (Development)

| Role | Username | Password | PIN |
| :--- | :--- | :--- | :--- |
| **Super Admin** | admin | admin123 | 000000 |
| **Ketua** | ketua | 123 | 123456 |
| **Hakim** | hakim | 123 | 123456 |

## 📝 Catatan Pengembangan
Proyek ini dikembangkan sebagai bagian dari tugas perkuliahan (Tugas UNSIA).

---
© 2026 - Pengadilan Agama Ibukota Nusantara
