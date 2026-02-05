# Technical Documentation

## Overview
This project is a modular Flask application for the PA IKN personnel and case management system.
It uses SQLite for storage, HTMX for no-reload UI updates, and a WebSocket endpoint (Flask-Sock)
for internal chat.

## Stack
- Flask (web framework)
- SQLite (database)
- HTMX (no-reload interactions)
- Flask-Sock (WebSocket for chat)
- Bootstrap 5 (UI)
- Flask-Smorest (OpenAPI/Swagger docs - legacy/api blueprint)
- Flask-Swagger + Swagger UI (OpenAPI 2.0 docs - core app)

## Project Structure
```
app/
  __init__.py          App factory, websocket setup, API docs init
  api.py               OpenAPI endpoints (flask-smorest)
  config.py            App configuration
  db.py                DB init and helpers
  errors.py            Error handlers
  utils.py             Helpers (uploads, validation)
  ws.py                WebSocket chat endpoint
  migrate_uuid.py      Migration script for UUIDs
  migrate_audit.py     Migration script for Audit/Soft Delete
  blueprints/
    auth.py            Login, captcha, pin verification
    public.py          Public pages
    dashboard.py       Dashboard pages + CRUD
    admin.py           Admin CRUD (pegawai, berita, galeri, pengaturan)
    export.py          Export endpoints
    uploads.py         Static upload serving
templates/
  dashboard_layout.html
  dashboard_*.html     Page-per-section dashboard views
  partials/            Reusable components
```

## Database
Database file: `perkara.db`

### Core Schema Updates
- **Primary Keys**: All tables now use **UUID** (string) instead of Integer IDs.
- **Audit & Soft Delete**: Core tables (`users`, `perkara`, `berita`, `galeri`, `laporan_tamu`, `diskusi`) include:
  - `is_deleted` (0/1)
  - `deleted_at` (Timestamp)
  - `created_at` (Timestamp)
  - `created_by` (Username)
  - `updated_at` (Timestamp)
  - `updated_by` (Username)

### Main Tables
- `users`
- `perkara`
- `diskusi`
- `laporan_tamu`
- `berita`
- `galeri`
- `pengaturan`

DB is initialized on app start via `init_db()` in `app/db.py`.

## Running Locally
```
python app.py
```
Default port: `5000`

## WebSocket Chat
Endpoint: `/chatroom`
Used by HTMX `ws` extension. Messages are stored in `diskusi` and broadcast to connected clients.

## HTMX No-Reload
All CRUD operations in dashboard/admin use HTMX:
- Forms use `hx-post` and return partial HTML or `204`.
- Deletes use `hx-get` with `hx-target="..."` (often utilizing the global Delete Modal).
- Toast notifications triggered via `HX-Trigger`.

## OpenAPI / Swagger
The application supports two Swagger documentations:
1. **Core App Docs** (`flask-swagger`):
   - UI: `/docs`
   - JSON: `/spec`
   - Covers standard Flask routes defined in blueprints.

2. **API Blueprint Docs** (`flask-smorest`):
   - UI: `/docs/swagger-ui`
   - JSON: `/docs/openapi.json`
   - Covers endpoints defined in `api.py`.

## Environment Variables
Konfigurasi melalui file `.env` (gunakan `.env.example` sebagai template):

| Variable | Default | Keterangan |
|----------|---------|------------|
| `SECRET_KEY` | `dev-secret-key...` | **Wajib diganti di production** |
| `DATABASE_PATH` | `perkara.db` | Path ke SQLite database |
| `UPLOAD_FOLDER` | `uploads` | Folder untuk upload files |
| `SHOW_TRACEBACK` | `false` | Set `true` untuk debug |

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Docker Deployment

### Build & Run
```bash
# Development
docker-compose up --build

# Production (detached)
docker-compose up -d --build
```

### Production Configuration
- **WSGI Server**: Gunicorn (2 workers, 4 threads)
- **Persistent Volumes**: `app_data` (database), `app_uploads` (files)
- **Health Check**: `/health` endpoint
- **Restart Policy**: `unless-stopped`

### Deploy ke VPS
```bash
# 1. Copy project
scp -r . user@vps:/app/sistem-pa

# 2. Setup environment
cd /app/sistem-pa
cp .env.example .env
nano .env  # Set SECRET_KEY

# 3. Run
docker-compose up -d --build

# 4. Monitor
docker-compose logs -f
```
