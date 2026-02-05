import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "perkara.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print("Starting migration to add Audit & Soft Delete columns...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    tables = [
        "users", "perkara", "berita", "galeri", "laporan_tamu", "diskusi", 
        "mediasi", "akta_cerai"
    ]

    columns = [
        ("is_deleted", "INTEGER DEFAULT 0"),
        ("deleted_at", "TEXT"),
        ("created_at", "TEXT"),
        ("created_by", "TEXT"),
        ("updated_at", "TEXT"),
        ("updated_by", "TEXT")
    ]

    for table in tables:
        print(f"Processing table: {table}")
        # Get existing columns
        try:
            cur_cols = [row[1] for row in c.execute(f"PRAGMA table_info({table})").fetchall()]
        except sqlite3.OperationalError:
            print(f"Table {table} does not exist, skipping.")
            continue

        for col_name, col_def in columns:
            if col_name not in cur_cols:
                try:
                    alter_query = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"
                    c.execute(alter_query)
                    print(f"  + Added column: {col_name}")
                except Exception as e:
                    print(f"  ! Error adding {col_name} to {table}: {e}")
            else:
                print(f"  = Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
