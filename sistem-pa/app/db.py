import sqlite3
from datetime import datetime

from flask import current_app, g
from .seed import seed_data


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = get_db()
    c = conn.cursor()

    # Core auth/users
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
        (id TEXT PRIMARY KEY, username TEXT, password TEXT, role TEXT,
        nama_lengkap TEXT, nip TEXT, pas_foto TEXT, pin_6digit TEXT, pdf_sk_pns TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)"""
    )

    # Perkara
    c.execute(
        """CREATE TABLE IF NOT EXISTS perkara
        (id TEXT PRIMARY KEY, no_perkara TEXT, nama_suami TEXT, nama_istri TEXT,
        keluhan TEXT, tanggal_daftar TEXT, nama_staff TEXT, file_suami TEXT,
        file_istri TEXT, status TEXT, biaya_daftar TEXT, no_akta_cerai TEXT,
        hasil_mediasi TEXT, detail_mediasi TEXT, nama_mediator TEXT, tanggal_sidang TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)"""
    )

    # Settings/CMS
    c.execute(
        """CREATE TABLE IF NOT EXISTS pengaturan
        (kunci TEXT PRIMARY KEY, nilai TEXT)"""
    )

    # Chat (legacy + charter)
    c.execute(
        """CREATE TABLE IF NOT EXISTS diskusi
        (id TEXT PRIMARY KEY, pengirim TEXT, role_pengirim TEXT, pesan TEXT, tanggal TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS chat
        (id TEXT PRIMARY KEY, pengirim TEXT, role_pengirim TEXT, pesan TEXT, tanggal TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)"""
    )

    # Public reports
    c.execute(
        """CREATE TABLE IF NOT EXISTS laporan_tamu
        (id TEXT PRIMARY KEY, nama_tamu TEXT, no_hp TEXT, isi_pesan TEXT,
        balasan TEXT, tanggal TEXT, status TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)"""
    )

    # News + Gallery
    c.execute(
        """CREATE TABLE IF NOT EXISTS berita
        (id TEXT PRIMARY KEY, judul TEXT, isi TEXT, gambar TEXT, tanggal TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS galeri
        (id TEXT PRIMARY KEY, judul_foto TEXT, file_foto TEXT, tanggal TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT)"""
    )

    # Charter expansion tables
    c.execute(
        """CREATE TABLE IF NOT EXISTS mediasi
        (id TEXT PRIMARY KEY, perkara_id TEXT, mediator TEXT, hasil TEXT,
        detail TEXT, tanggal TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS akta_cerai
        (id TEXT PRIMARY KEY, perkara_id TEXT, nomor TEXT, tanggal_terbit TEXT,
        penerima TEXT, file_pdf TEXT, barcode_ttd TEXT,
        is_deleted INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT, created_by TEXT, updated_at TEXT, updated_by TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS dokumen
        (id TEXT PRIMARY KEY, perkara_id TEXT, jenis TEXT, path TEXT,
        created_at TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS pegawai
        (id TEXT PRIMARY KEY, user_id TEXT, nama_lengkap TEXT, nip TEXT,
        jabatan TEXT, pas_foto TEXT, created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id))"""
    )

    seed_data(conn)


def init_app(app):
    app.teardown_appcontext(close_db)
