import sqlite3
from datetime import datetime

from flask import current_app, g

from .utils import get_default_logo


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


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def init_db():
    conn = get_db()
    c = conn.cursor()

    # Core auth/users
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT,
        nama_lengkap TEXT, nip TEXT, pas_foto TEXT, pin_6digit TEXT, pdf_sk_pns TEXT)"""
    )

    # Perkara
    c.execute(
        """CREATE TABLE IF NOT EXISTS perkara
        (id INTEGER PRIMARY KEY, no_perkara TEXT, nama_suami TEXT, nama_istri TEXT,
        keluhan TEXT, tanggal_daftar TEXT, nama_staff TEXT, file_suami TEXT,
        file_istri TEXT, status TEXT, biaya_daftar TEXT, no_akta_cerai TEXT,
        hasil_mediasi TEXT, detail_mediasi TEXT, nama_mediator TEXT, tanggal_sidang TEXT)"""
    )

    # Settings/CMS
    c.execute(
        """CREATE TABLE IF NOT EXISTS pengaturan
        (kunci TEXT PRIMARY KEY, nilai TEXT)"""
    )

    # Chat (legacy + charter)
    c.execute(
        """CREATE TABLE IF NOT EXISTS diskusi
        (id INTEGER PRIMARY KEY, pengirim TEXT, role_pengirim TEXT, pesan TEXT, tanggal TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS chat
        (id INTEGER PRIMARY KEY, pengirim TEXT, role_pengirim TEXT, pesan TEXT, tanggal TEXT)"""
    )

    # Public reports
    c.execute(
        """CREATE TABLE IF NOT EXISTS laporan_tamu
        (id INTEGER PRIMARY KEY, nama_tamu TEXT, no_hp TEXT, isi_pesan TEXT,
        balasan TEXT, tanggal TEXT, status TEXT)"""
    )

    # News + Gallery
    c.execute(
        """CREATE TABLE IF NOT EXISTS berita
        (id INTEGER PRIMARY KEY, judul TEXT, isi TEXT, gambar TEXT, tanggal TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS galeri
        (id INTEGER PRIMARY KEY, judul_foto TEXT, file_foto TEXT, tanggal TEXT)"""
    )

    # Charter expansion tables
    c.execute(
        """CREATE TABLE IF NOT EXISTS mediasi
        (id INTEGER PRIMARY KEY, perkara_id INTEGER, mediator TEXT, hasil TEXT,
        detail TEXT, tanggal TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS akta_cerai
        (id INTEGER PRIMARY KEY, perkara_id INTEGER, nomor TEXT, tanggal_terbit TEXT,
        penerima TEXT, file_pdf TEXT, barcode_ttd TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS dokumen
        (id INTEGER PRIMARY KEY, perkara_id INTEGER, jenis TEXT, path TEXT,
        created_at TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS pegawai
        (id INTEGER PRIMARY KEY, user_id INTEGER, nama_lengkap TEXT, nip TEXT,
        jabatan TEXT, pas_foto TEXT, created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id))"""
    )

    # Default settings
    c.execute("SELECT count(*) FROM pengaturan")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT OR IGNORE INTO pengaturan VALUES (?, ?)",
            (
                "bg_landing",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Mahkamah_Agung_Republik_Indonesia.jpg/1200px-Mahkamah_Agung_Republik_Indonesia.jpg",
            ),
        )
        c.execute(
            "INSERT OR IGNORE INTO pengaturan VALUES (?, ?)",
            (
                "bg_login",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Mahkamah_Agung_Republik_Indonesia.jpg/1200px-Mahkamah_Agung_Republik_Indonesia.jpg",
            ),
        )
        c.execute(
            "INSERT OR IGNORE INTO pengaturan VALUES (?, ?)",
            (
                "bg_dashboard",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Mahkamah_Agung_Republik_Indonesia.jpg/1200px-Mahkamah_Agung_Republik_Indonesia.jpg",
            ),
        )
        c.execute(
            "INSERT OR IGNORE INTO pengaturan VALUES (?, ?)",
            (
                "bg_verify_pin",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Mahkamah_Agung_Republik_Indonesia.jpg/1200px-Mahkamah_Agung_Republik_Indonesia.jpg",
            ),
        )
        c.execute(
            "INSERT OR IGNORE INTO pengaturan VALUES (?, ?)",
            ("foto_ketua", "https://via.placeholder.com/300x300?text=FOTO+KETUA"),
        )
        c.execute("INSERT OR IGNORE INTO pengaturan VALUES (?, ?)", ("logo_web", get_default_logo()))
        c.execute("INSERT OR IGNORE INTO pengaturan VALUES (?, ?)", ("logo_pa_ikn", ""))
        c.execute("INSERT OR IGNORE INTO pengaturan VALUES (?, ?)", ("barcode_ttd", ""))
        sambutan_text = (
            "Assalamu'alaikum Warahmatullahi Wabarakatuh, puji syukur kehadirat Allah SWT "
            "atas hadirnya laman resmi ini sebagai wujud transformasi layanan peradilan di era baru "
            "Ibu Kota Nusantara."
        )
        c.execute("INSERT OR IGNORE INTO pengaturan VALUES (?, ?)", ("sambutan_ketua", sambutan_text))
        c.execute("INSERT OR IGNORE INTO pengaturan VALUES (?, ?)", ("no_telp", "(021) 123-4567"))
        c.execute("INSERT OR IGNORE INTO pengaturan VALUES (?, ?)", ("email_kantor", "info@pa-ikn.go.id"))
        for i in range(1, 6):
            c.execute(
                "INSERT OR IGNORE INTO pengaturan VALUES (?, ?)",
                (f"kegiatan_{i}", "https://via.placeholder.com/400x300?text=Kegiatan+Kantor"),
            )

    # Seed users
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("admin", "admin123", "admin_it", "Super Admin IT", "999999", "", "000000", ""),
        )
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("ketua", "123", "ketua", "Dr. Ketua Pengadilan, S.H., M.H.", "199001", "", "123456", ""),
        )
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("wakil", "123", "wakil_ketua", "Wakil Ketua, S.Ag.", "199002", "", "123456", ""),
        )
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("panitera", "123", "panitera", "Panitera Utama", "199003", "", "123456", ""),
        )
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("sekretaris", "123", "sekretaris", "Sekretaris Jenderal", "199004", "", "123456", ""),
        )
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("kassubag", "123", "kassubag", "Kassubag Kepegawaian", "199005", "", "123456", ""),
        )
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("hakim", "123", "hakim", "Hakim Mediator", "199006", "", "123456", ""),
        )
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("staff", "123", "staff", "Staff Pelayanan", "199007", "", "123456", ""),
        )

    # Seed berita if empty
    c.execute("SELECT count(*) FROM berita")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d")
        c.execute(
            "INSERT INTO berita VALUES (NULL, ?, ?, ?, ?)",
            ("Rapat Koordinasi Tahunan", "Pengadilan Agama IKN mengadakan rapat tahunan untuk evaluasi kinerja.", "https://via.placeholder.com/150", now),
        )
        c.execute(
            "INSERT INTO berita VALUES (NULL, ?, ?, ?, ?)",
            ("Kunjungan Mahkamah Agung", "Delegasi MA meninjau lokasi gedung baru di IKN.", "https://via.placeholder.com/150", now),
        )
        c.execute(
            "INSERT INTO berita VALUES (NULL, ?, ?, ?, ?)",
            ("Sosialisasi Hukum Keluarga", "Hakim memberikan penyuluhan kepada masyarakat sekitar.", "https://via.placeholder.com/150", now),
        )

    # Backfill pegawai from users if empty
    if _table_exists(conn, "pegawai"):
        c.execute("SELECT count(*) FROM pegawai")
        if c.fetchone()[0] == 0:
            rows = c.execute("SELECT id, nama_lengkap, nip, role, pas_foto FROM users").fetchall()
            for row in rows:
                c.execute(
                    "INSERT INTO pegawai (user_id, nama_lengkap, nip, jabatan, pas_foto, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (row["id"], row["nama_lengkap"], row["nip"], row["role"], row["pas_foto"], datetime.now().strftime("%Y-%m-%d %H:%M")),
                )

    conn.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
