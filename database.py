import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# En production sur Render, DB_PATH pointe vers le Persistent Disk (/data)
# En local, utilise restaurant.db dans le dossier du projet
DB_PATH = os.environ.get(
    'DB_PATH',
    os.path.join(BASE_DIR, 'restaurant.db')
)

# S'assurer que le dossier parent existe (utile pour /data sur Render)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # concurrent reads + writes
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

    # Migration: add image_path if upgrading from older schema
    try:
        c.execute("ALTER TABLE menu_items ADD COLUMN image_path TEXT DEFAULT ''")
    except Exception:
        pass

    conn.commit()
    conn.close()
    print("✅ Base de données initialisée →", DB_PATH)
