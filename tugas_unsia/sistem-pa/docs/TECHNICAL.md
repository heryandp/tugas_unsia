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
- Flask-Smorest (OpenAPI/Swagger docs)

## Project Structure
```
app/
  __init__.py          App factory, websocket setup, API docs init
  api.py               OpenAPI endpoints (read-only list/detail)
  config.py            App configuration
  db.py                DB init and helpers
  errors.py            Error handlers
  utils.py             Helpers (uploads, validation)
  ws.py                WebSocket chat endpoint
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

Main tables:
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
- Deletes use `hx-get` with `hx-target="closest ..."` and `hx-swap="outerHTML"`.
- Toast notifications triggered via `HX-Trigger`.

## OpenAPI / Swagger
Swagger UI: `/docs/swagger-ui`
OpenAPI JSON: `/docs/openapi.json`

These are powered by Flask-Smorest and expose read-only API endpoints.
