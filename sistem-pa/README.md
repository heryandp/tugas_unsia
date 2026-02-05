# 🏛️ Sistem Informasi Pengadilan Agama Ibukota Nusantara (Sistem-PA IKN)

[![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952b3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![HTMX](https://img.shields.io/badge/HTMX-1.9-3366cc?style=for-the-badge)](https://htmx.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

Sistem informasi terintegrasi untuk mendukung manajemen perkara perceraian di Pengadilan Agama Ibukota Nusantara. Berfokus pada otomasi proses, keamanan berlapis (2FA-like PIN), dan transparansi pelayanan publik menggunakan teknologi web modern.

---

## 🚀 Fitur Utama

-   **⚡ HTMX No-Reload UI**: Pengalaman pengguna yang mulus tanpa refresh halaman pada setiap aksi CRUD.
-   **💬 Real-time Chatroom**: Komunikasi internal antar pegawai berbasis WebSockets (Flask-Sock).
-   **📑 Manajemen Perkara & Akta**: Pendaftaran, pelacakan, dan penerbitan otomatis dokumen hukum (PDF/Word).
-   **🛡️ Keamanan Berlapis**: Autentikasi ganda (Password + PIN 6-Digit) untuk perlindungan data sensitif.
-   **📊 Dashboard Multi-Role**: Hak akses spesifik untuk Admin IT, Ketua, Hakim, Panitera, Staff, dan Publik.
-   **🌐 Pelayanan Publik**: Portal mandiri untuk masyarakat mengecek jadwal sidang dan profil pegawai.
-   **🔍 Auto-Generated API Docs**: Dokumentasi API interaktif menggunakan Swagger UI.

---

## 🛠️ Tech Stack

-   **Backend**: Python 3.11, Flask
-   **Database**: SQLite (UUID-based PKs, Soft Delete, Audit Columns)
-   **Frontend**: HTML5, CSS3, Bootstrap 5, HTMX
-   **Docs**: Flask-Swagger, Flask-Smorest (OpenAPI Spec)
-   **Deployment**: Gunicorn (WSGI), Docker, Nginx

---

## 📦 Instalasi & Pengoperasian

### Running Locally (Development)

1. **Clone Repo & Masuk ke Folder**
   ```bash
   git clone https://github.com/heryandp/tugas_unsia.git
   cd tugas_unsia/sistem-pa
   ```

2. **Setup .env**
   ```bash
   cp .env.example .env
   # Edit .env dan masukkan SECRET_KEY
   ```

3. **Install & Run**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

### Running via Docker (Production)

```bash
# Build & Run Detached
docker-compose up -d --build
```
Aplikasi akan berjalan di port `5000` dengan persistent volume untuk database dan media upload.

---

## 📖 Dokumentasi API

Interaksi API dapat dipelajari melalui Swagger UI yang tersedia di:
-   **Core App Docs**: `http://localhost:5000/docs`
-   **API Blueprint**: `http://localhost:5000/docs/swagger-ui`
-   **JSON Spec**: `/spec` atau `/docs/openapi.json`

---

## 🔐 Kredensial Default

| Role | Username | Password | PIN |
| :--- | :--- | :--- | :--- |
| **Admin IT** | `admin` | `admin123` | `000000` |
| **Ketua** | `ketua` | `123` | `123456` |
| **Staff** | `staff` | `123` | `123456` |

---

## � Dokumentasi Teknis
Detail lebih lanjut mengenai arsitektur, skema database, dan panduan deployment dapat ditemukan di folder `docs/`:
-   [`PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md)
-   [`TECHNICAL.md`](docs/TECHNICAL.md)
-   [`API.md`](docs/API.md)

---
© 2026 - Pengadilan Agama Ibukota Nusantara
