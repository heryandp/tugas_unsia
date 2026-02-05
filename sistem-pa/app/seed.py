import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash
from .utils import get_default_logo

def seed_data(conn):
    c = conn.cursor()

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
                (f"kegiatan_{i}", f"https://placehold.co/400x300?text=Kegiatan+{i}"),
            )

    # Seed users
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Columns: id, username, password, role, nama_lengkap, nip, pas_foto, pin_6digit, pdf_sk_pns,
        #          is_deleted, deleted_at, created_at, created_by, updated_at, updated_by
        users = [
            (str(uuid.uuid4()), "admin", generate_password_hash("admin123"), "admin_it", "Super Admin IT", "999999", "", "000000", "", 0, None, now, "system", None, None),
            (str(uuid.uuid4()), "ketua", generate_password_hash("123"), "ketua", "Dr. Ketua Pengadilan, S.H., M.H.", "199001", "", "123456", "", 0, None, now, "system", None, None),
            (str(uuid.uuid4()), "wakil", generate_password_hash("123"), "wakil_ketua", "Wakil Ketua, S.Ag.", "199002", "", "123456", "", 0, None, now, "system", None, None),
            (str(uuid.uuid4()), "panitera", generate_password_hash("123"), "panitera", "Panitera Utama", "199003", "", "123456", "", 0, None, now, "system", None, None),
            (str(uuid.uuid4()), "sekretaris", generate_password_hash("123"), "sekretaris", "Sekretaris Jenderal", "199004", "", "123456", "", 0, None, now, "system", None, None),
            (str(uuid.uuid4()), "kassubag", generate_password_hash("123"), "kassubag", "Kassubag Kepegawaian", "199005", "", "123456", "", 0, None, now, "system", None, None),
            (str(uuid.uuid4()), "hakim", generate_password_hash("123"), "hakim", "Hakim Mediator", "199006", "", "123456", "", 0, None, now, "system", None, None),
            (str(uuid.uuid4()), "staff", generate_password_hash("123"), "staff", "Staff Pelayanan", "199007", "", "123456", "", 0, None, now, "system", None, None),
        ]
        c.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", users)

    # Seed berita if empty
    c.execute("SELECT count(*) FROM berita")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d")
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Columns: id, judul, isi, gambar, tanggal, is_deleted, deleted_at, created_at, created_by, updated_at, updated_by
        berita = [
            (str(uuid.uuid4()), "Rapat Koordinasi Tahunan", "Pengadilan Agama IKN mengadakan rapat tahunan untuk evaluasi kinerja.", "https://via.placeholder.com/150", now, 0, None, now_ts, "system", None, None),
            (str(uuid.uuid4()), "Kunjungan Mahkamah Agung", "Delegasi MA meninjau lokasi gedung baru di IKN.", "https://via.placeholder.com/150", now, 0, None, now_ts, "system", None, None),
            (str(uuid.uuid4()), "Sosialisasi Hukum Keluarga", "Hakim memberikan penyuluhan kepada masyarakat sekitar.", "https://via.placeholder.com/150", now, 0, None, now_ts, "system", None, None),
        ]
        c.executemany("INSERT INTO berita VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", berita)

    # Backfill pegawai from users if empty (Logic similar to original, but using UUID for relation)
    # Check if table exists first (it should, as init_db calls create)
    c.execute("SELECT count(*) FROM pegawai")
    if c.fetchone()[0] == 0:
        rows = c.execute("SELECT id, nama_lengkap, nip, role, pas_foto FROM users").fetchall()
        for row in rows:
            c.execute(
                "INSERT INTO pegawai (id, user_id, nama_lengkap, nip, jabatan, pas_foto, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), row["id"], row["nama_lengkap"], row["nip"], row["role"], row["pas_foto"], datetime.now().strftime("%Y-%m-%d %H:%M")),
            )

    conn.commit()
