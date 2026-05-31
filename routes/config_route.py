import json, os
from flask import Blueprint, jsonify, request

config_bp  = Blueprint('config', __name__)
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

ALLOWED_KEYS = {
    'restaurant_name', 'tagline', 'logo_emoji', 'welcome_message',
    'welcome_sub', 'whatsapp_number', 'address', 'phone',
    'hours_lunch', 'hours_dinner',
}


def _load():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


@config_bp.route('/config', methods=['GET'])
def get_config():
    return jsonify(_load())


@config_bp.route('/config', methods=['POST'])
def update_config():
    data = request.get_json(silent=True) or {}
    cfg  = _load()

    for key in ALLOWED_KEYS:
        if key in data and isinstance(data[key], str):
            cfg[key] = data[key].strip()

    # Nested colors object
    if 'colors' in data and isinstance(data['colors'], dict):
        for k in ('primary', 'primary_light'):
            val = data['colors'].get(k, '').strip()
            if val.startswith('#') and len(val) in (4, 7):
                cfg.setdefault('colors', {})[k] = val

    _save(cfg)
    return jsonify({'message': 'Configuration sauvegardée', 'config': cfg})
