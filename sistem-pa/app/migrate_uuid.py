import sqlite3
import shutil
import uuid
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_PATH = "perkara.db"
BACKUP_PATH = "perkara.db.bak"

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    print(f"Backing up {DB_PATH} to {BACKUP_PATH}...")
    shutil.copy2(DB_PATH, BACKUP_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    tables = ["users", "perkara", "pengaturan", "diskusi", "chat", "laporan_tamu", "berita", "galeri", "mediasi", "akta_cerai", "dokumen", "pegawai"]
    
    # helper to check if table exists
    def table_exists(name):
        return c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None

    print("Renaming existing tables...")
    for table in tables:
        if table_exists(table):
            c.execute(f"ALTER TABLE {table} RENAME TO {table}_old")

    print("Creating new tables with UUID schema...")
    
    # Re-create tables with TEXT PRIMARY KEY (UUID)
    c.execute("""CREATE TABLE IF NOT EXISTS users
        (id TEXT PRIMARY KEY, username TEXT, password TEXT, role TEXT,
        nama_lengkap TEXT, nip TEXT, pas_foto TEXT, pin_6digit TEXT, pdf_sk_pns TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS perkara
        (id TEXT PRIMARY KEY, no_perkara TEXT, nama_suami TEXT, nama_istri TEXT,
        keluhan TEXT, tanggal_daftar TEXT, nama_staff TEXT, file_suami TEXT,
        file_istri TEXT, status TEXT, biaya_daftar TEXT, no_akta_cerai TEXT,
        hasil_mediasi TEXT, detail_mediasi TEXT, nama_mediator TEXT, tanggal_sidang TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS pengaturan
        (kunci TEXT PRIMARY KEY, nilai TEXT)""") # Key is already text, but good to ensure

    c.execute("""CREATE TABLE IF NOT EXISTS diskusi
        (id TEXT PRIMARY KEY, pengirim TEXT, role_pengirim TEXT, pesan TEXT, tanggal TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS chat
        (id TEXT PRIMARY KEY, pengirim TEXT, role_pengirim TEXT, pesan TEXT, tanggal TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS laporan_tamu
        (id TEXT PRIMARY KEY, nama_tamu TEXT, no_hp TEXT, isi_pesan TEXT,
        balasan TEXT, tanggal TEXT, status TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS berita
        (id TEXT PRIMARY KEY, judul TEXT, isi TEXT, gambar TEXT, tanggal TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS galeri
        (id TEXT PRIMARY KEY, judul_foto TEXT, file_foto TEXT, tanggal TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS mediasi
        (id TEXT PRIMARY KEY, perkara_id TEXT, mediator TEXT, hasil TEXT,
        detail TEXT, tanggal TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS akta_cerai
        (id TEXT PRIMARY KEY, perkara_id TEXT, nomor TEXT, tanggal_terbit TEXT,
        penerima TEXT, file_pdf TEXT, barcode_ttd TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS dokumen
        (id TEXT PRIMARY KEY, perkara_id TEXT, jenis TEXT, path TEXT,
        created_at TEXT,
        FOREIGN KEY(perkara_id) REFERENCES perkara(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS pegawai
        (id TEXT PRIMARY KEY, user_id TEXT, nama_lengkap TEXT, nip TEXT,
        jabatan TEXT, pas_foto TEXT, created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id))""")

    # Mappings old_id -> new_uuid
    user_map = {}
    perkara_map = {}

    print("Migrating data...")

    # Users
    if table_exists("users_old"):
        rows = c.execute("SELECT * FROM users_old").fetchall()
        for row in rows:
            new_id = str(uuid.uuid4())
            user_map[row['id']] = new_id
            # Hash the password if it's not already hashed (simplistic check, but sufficient for this specific migration from plain text)
            # In a real scenario, we might want to check the prefix, but here we assume all old are plain text
            hashed_pw = generate_password_hash(row['password'])
            c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",
                      (new_id, row['username'], hashed_pw, row['role'], row['nama_lengkap'], row['nip'], row['pas_foto'], row['pin_6digit'], row['pdf_sk_pns']))

    # Perkara
    if table_exists("perkara_old"):
        rows = c.execute("SELECT * FROM perkara_old").fetchall()
        for row in rows:
            new_id = str(uuid.uuid4())
            perkara_map[row['id']] = new_id
            c.execute("INSERT INTO perkara VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (new_id, row['no_perkara'], row['nama_suami'], row['nama_istri'], row['keluhan'], row['tanggal_daftar'], row['nama_staff'], row['file_suami'], row['file_istri'], row['status'], row['biaya_daftar'], row['no_akta_cerai'], row['hasil_mediasi'], row['detail_mediasi'], row['nama_mediator'], row['tanggal_sidang']))

    # Pengaturan (Key is PK, just copy)
    if table_exists("pengaturan_old"):
        rows = c.execute("SELECT * FROM pengaturan_old").fetchall()
        for row in rows:
            c.execute("INSERT INTO pengaturan VALUES (?,?)", (row['kunci'], row['nilai']))

    # Simple tables (just need new UUID PK)
    simple_tables = ["diskusi", "chat", "laporan_tamu", "berita", "galeri"]
    for tbl in simple_tables:
        if table_exists(f"{tbl}_old"):
            rows = c.execute(f"SELECT * FROM {tbl}_old").fetchall()
            cols = [col[1] for col in c.execute(f"PRAGMA table_info({tbl}_old)").fetchall() if col[1] != 'id']
            placeholders = ",".join(["?"] * (len(cols) + 1))
            col_names = ",".join(cols)
            for row in rows:
                new_id = str(uuid.uuid4())
                values = [new_id] + [row[col] for col in cols]
                c.execute(f"INSERT INTO {tbl} VALUES ({placeholders})", values)

    # Tables with Foreign Keys
    # Mediasi (perkara_id)
    if table_exists("mediasi_old"):
        rows = c.execute("SELECT * FROM mediasi_old").fetchall()
        for row in rows:
            new_id = str(uuid.uuid4())
            new_pid = perkara_map.get(row['perkara_id'])
            if new_pid:
                c.execute("INSERT INTO mediasi VALUES (?,?,?,?,?,?)",
                          (new_id, new_pid, row['mediator'], row['hasil'], row['detail'], row['tanggal']))

    # Akta Cerai (perkara_id)
    if table_exists("akta_cerai_old"):
        rows = c.execute("SELECT * FROM akta_cerai_old").fetchall()
        for row in rows:
            new_id = str(uuid.uuid4())
            new_pid = perkara_map.get(row['perkara_id'])
            if new_pid:
                c.execute("INSERT INTO akta_cerai VALUES (?,?,?,?,?,?,?)",
                          (new_id, new_pid, row['nomor'], row['tanggal_terbit'], row['penerima'], row['file_pdf'], row['barcode_ttd']))

    # Dokumen (perkara_id)
    if table_exists("dokumen_old"):
        rows = c.execute("SELECT * FROM dokumen_old").fetchall()
        for row in rows:
            new_id = str(uuid.uuid4())
            new_pid = perkara_map.get(row['perkara_id'])
            if new_pid:
                c.execute("INSERT INTO dokumen VALUES (?,?,?,?,?)",
                          (new_id, new_pid, row['jenis'], row['path'], row['created_at']))

    # Pegawai (user_id)
    if table_exists("pegawai_old"):
        rows = c.execute("SELECT * FROM pegawai_old").fetchall()
        for row in rows:
            new_id = str(uuid.uuid4())
            new_uid = user_map.get(row['user_id'])
            if new_uid:
                c.execute("INSERT INTO pegawai VALUES (?,?,?,?,?,?,?)",
                          (new_id, new_uid, row['nama_lengkap'], row['nip'], row['jabatan'], row['pas_foto'], row['created_at']))

    print("Cleaning up old tables...")
    for table in tables:
        if table_exists(f"{table}_old"):
            c.execute(f"DROP TABLE {table}_old")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
