import os
from database import get_db

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR  = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

VALID_ORDER_STATUSES = ('pending', 'confirmed', 'done')
VALID_RES_STATUSES   = ('pending', 'confirmed', 'cancelled')


# ═══════════════════════════════════════════════════════════════════
# ORDERS
# ═══════════════════════════════════════════════════════════════════

def get_all_orders():
    conn = get_db()
    rows = conn.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_order(data):
    conn = get_db()
    conn.execute(
        '''INSERT INTO orders (customer_name, items, delivery_type, pickup_time, phone, status)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (
            (data.get('customer_name') or 'Anonyme').strip(),
            (data.get('items') or '').strip(),
            (data.get('delivery_type') or 'sur place').strip(),
            (data.get('pickup_time') or '').strip(),
            (data.get('phone') or '').strip(),
            data.get('status') or 'pending',
        )
    )
    conn.commit()
    conn.close()


def update_order_status(order_id, status):
    if status not in VALID_ORDER_STATUSES:
        raise ValueError(f'Invalid status: {status}')
    conn = get_db()
    conn.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
# RESERVATIONS
# ═══════════════════════════════════════════════════════════════════

def get_all_reservations():
    conn = get_db()
    rows = conn.execute('SELECT * FROM reservations ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_reservation(data):
    conn = get_db()
    conn.execute(
        '''INSERT INTO reservations (customer_name, party_size, reservation_time, phone, status)
           VALUES (?, ?, ?, ?, ?)''',
        (
            (data.get('customer_name') or 'Anonyme').strip(),
            int(data.get('party_size') or 2),
            (data.get('reservation_time') or '').strip(),
            (data.get('phone') or '').strip(),
            data.get('status') or 'pending',
        )
    )
    conn.commit()
    conn.close()


def update_reservation_status(res_id, status):
    if status not in VALID_RES_STATUSES:
        raise ValueError(f'Invalid status: {status}')
    conn = get_db()
    conn.execute('UPDATE reservations SET status=? WHERE id=?', (status, res_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
# MENU
# ═══════════════════════════════════════════════════════════════════

def get_menu_items(all_items=False):
    conn = get_db()
    if all_items:
        rows = conn.execute(
            'SELECT * FROM menu_items ORDER BY category, position, id'
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM menu_items WHERE available=1 ORDER BY category, position, id'
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_menu_item(data):
    conn = get_db()
    conn.execute(
        '''INSERT INTO menu_items (name, description, price, category, available, featured, position, image_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            (data.get('name') or '').strip(),
            (data.get('description') or '').strip(),
            float(data.get('price') or 0),
            (data.get('category') or 'Plats principaux').strip(),
            1 if data.get('available', True) else 0,
            1 if data.get('featured') else 0,
            int(data.get('position') or 0),
            (data.get('image_path') or '').strip(),
        )
    )
    conn.commit()
    conn.close()


def update_menu_item(item_id, data):
    """Partial update — only touches keys present in data."""
    ALLOWED = {
        'name': str, 'description': str, 'price': float,
        'category': str, 'available': int, 'featured': int,
        'position': int, 'image_path': str,
    }
    fields, values = [], []
    for field, cast in ALLOWED.items():
        if field not in data:
            continue
        val = data[field]
        if cast == float:
            val = float(val)
        elif cast == int:
            val = 1 if val else 0
        else:
            val = str(val).strip()
        fields.append(f'{field}=?')
        values.append(val)
    if not fields:
        return
    values.append(item_id)
    conn = get_db()
    conn.execute(f'UPDATE menu_items SET {", ".join(fields)} WHERE id=?', values)
    conn.commit()
    conn.close()


def delete_menu_item(item_id):
    # Clean up image file if any
    conn = get_db()
    row = conn.execute('SELECT image_path FROM menu_items WHERE id=?', (item_id,)).fetchone()
    if row and row['image_path']:
        fpath = os.path.join(BASE_DIR, 'static', row['image_path'].lstrip('/'))
        try:
            os.remove(fpath)
        except OSError:
            pass
    conn.execute('DELETE FROM menu_items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()


def reorder_menu_items(ordered_ids: list):
    """Set position by list order."""
    conn = get_db()
    for pos, item_id in enumerate(ordered_ids):
        conn.execute('UPDATE menu_items SET position=? WHERE id=?', (pos, item_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════

def get_stats():
    conn = get_db()
    q = conn.execute('''
        SELECT
            SUM(date(created_at)=date('now'))                                  AS today_orders,
            SUM(date(created_at)=date('now') AND status='done')                AS done_today,
            SUM(status='pending')                                               AS pending_orders,
            COUNT(*)                                                            AS total_orders
        FROM orders
    ''').fetchone()
    r = conn.execute('''
        SELECT
            SUM(date(created_at)=date('now')) AS today_reservations,
            COUNT(*)                           AS total_reservations
        FROM reservations
    ''').fetchone()
    conn.close()
    return {
        'today_orders':       int(q['today_orders']       or 0),
        'done_today':         int(q['done_today']         or 0),
        'pending_orders':     int(q['pending_orders']     or 0),
        'total_orders':       int(q['total_orders']       or 0),
        'today_reservations': int(r['today_reservations'] or 0),
        'total_reservations': int(r['total_reservations'] or 0),
    }
