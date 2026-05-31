import os
from flask import Flask, jsonify
from database import init_db
from routes.orders       import orders_bp
from routes.reservations import reservations_bp
from routes.webhook      import webhook_bp
from routes.pages        import pages_bp
from routes.menu         import menu_bp
from routes.stats        import stats_bp
from routes.config_route import config_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key           = os.environ.get('SECRET_KEY', 'restaurant-os-dev-key-change-in-prod')
app.json.ensure_ascii    = False
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024   # 4 MB upload limit

app.register_blueprint(orders_bp)
app.register_blueprint(reservations_bp)
app.register_blueprint(webhook_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(config_bp)


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route introuvable'}), 404


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Fichier trop volumineux (max 4 Mo)'}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Erreur serveur interne'}), 500


# ── Initialisation automatique ───────────────────────────────────────────────
# Appelé ici au niveau module = fonctionne avec gunicorn ET python app.py
init_db()

# Auto-seed si la base est vide (premier déploiement sur Render)
def _auto_seed():
    try:
        from database import get_db
        conn = get_db()
        empty = conn.execute('SELECT COUNT(*) FROM menu_items').fetchone()[0] == 0
        conn.close()
        if empty:
            from seed import seed
            seed()
            print("✅ Auto-seed exécuté (première installation)")
    except Exception as e:
        print(f"⚠️  Auto-seed ignoré : {e}")

_auto_seed()
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == '__main__':
    port  = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print("\n" + "="*52)
    print("  🍽️  Restaurant OS V1  —  Serveur démarré !")
    print("="*52)
    print(f"  Site client  →  http://localhost:{port}")
    print(f"  Dashboard    →  http://localhost:{port}/admin")
    print(f"  QR Code      →  http://localhost:{port}/qr")
    print("="*52 + "\n")
    app.run(debug=debug, port=port, host='0.0.0.0')
