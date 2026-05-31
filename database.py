import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Production Render → DB_PATH=/data/restaurant.db (Persistent Disk)
# Local → restaurant.db dans le dossier du projet
_requested = os.environ.get(
    'DB_PATH',
    os.path.join(BASE_DIR, 'restaurant.db')
)

# Tenter de créer le dossier parent — fallback si /data non monté
_db_dir = os.path.dirname(_requested)
try:
    if _db_dir:
        os.makedirs(_db_dir, exist_ok=True)
    DB_PATH = _requested
except (PermissionError, OSError):
    DB_PATH = os.path.join(BASE_DIR, 'restaurant.db')
    print(f"⚠️  /data inaccessible, fallback → {DB_PATH}")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT    NOT NULL,
            items         TEXT    NOT NULL,
            delivery_type TEXT    DEFAULT 'sur place',
            pickup_time   TEXT    DEFAULT '',
            status        TEXT    DEFAULT 'pending',
            phone         TEXT    DEFAULT '',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name    TEXT    NOT NULL,
            party_size       INTEGER NOT NULL DEFAULT 2,
            reservation_time TEXT    NOT NULL,
            status           TEXT    DEFAULT 'pending',
            phone            TEXT    DEFAULT '',
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            price       REAL    NOT NULL DEFAULT 0,
            category    TEXT    NOT NULL DEFAULT 'Plats principaux',
            available   INTEGER DEFAULT 1,
            featured    INTEGER DEFAULT 0,
            position    INTEGER DEFAULT 0,
            image_path  TEXT    DEFAULT ''
        )
    ''')

    try:
        c.execute("ALTER TABLE menu_items ADD COLUMN image_path TEXT DEFAULT ''")
    except Exception:
        pass

    conn.commit()
    conn.close()
    print("✅ Base de données initialisée →", DB_PATH)
