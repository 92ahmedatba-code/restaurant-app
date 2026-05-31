import os, uuid
from flask import Blueprint, request, jsonify, current_app
from services import (
    get_menu_items, create_menu_item, update_menu_item,
    delete_menu_item, reorder_menu_items, BASE_DIR, UPLOADS_DIR,
)

menu_bp = Blueprint('menu', __name__)

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_IMAGE_BYTES = 4 * 1024 * 1024   # 4 MB


def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@menu_bp.route('/menu', methods=['GET'])
def list_menu():
    all_items = request.args.get('all') == '1'
    return jsonify(get_menu_items(all_items=all_items))


@menu_bp.route('/menu', methods=['POST'])
def new_menu_item():
    data = request.get_json(silent=True) or {}
    name  = (data.get('name') or '').strip()
    price = data.get('price')
    if not name:
        return jsonify({'error': 'Le nom est requis'}), 400
    if price is None:
        return jsonify({'error': 'Le prix est requis'}), 400
    try:
        float(price)
    except (TypeError, ValueError):
        return jsonify({'error': 'Prix invalide'}), 400
    create_menu_item(data)
    return jsonify({'message': 'Plat ajouté avec succès'}), 201


@menu_bp.route('/menu/<int:item_id>', methods=['PATCH'])
def patch_menu_item(item_id):
    data = request.get_json(silent=True) or {}
    if 'price' in data:
        try:
            float(data['price'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Prix invalide'}), 400
    update_menu_item(item_id, data)
    return jsonify({'message': 'Plat mis à jour'})


@menu_bp.route('/menu/<int:item_id>', methods=['DELETE'])
def remove_menu_item(item_id):
    delete_menu_item(item_id)
    return jsonify({'message': 'Plat supprimé'})


@menu_bp.route('/menu/reorder', methods=['POST'])
def reorder():
    data = request.get_json(silent=True) or {}
    ids  = data.get('ids', [])
    if not isinstance(ids, list):
        return jsonify({'error': 'ids doit être une liste'}), 400
    reorder_menu_items([int(i) for i in ids])
    return jsonify({'message': 'Ordre mis à jour'})


@menu_bp.route('/menu/<int:item_id>/image', methods=['POST'])
def upload_image(item_id):
    if 'image' not in request.files:
        return jsonify({'error': 'Aucun fichier reçu'}), 400
    file = request.files['image']
    if not file.filename:
        return jsonify({'error': 'Nom de fichier manquant'}), 400
    if not _allowed(file.filename):
        return jsonify({'error': 'Format non supporté. Utilisez JPG, PNG ou WebP'}), 400

    # Read & check size
    data = file.read()
    if len(data) > MAX_IMAGE_BYTES:
        return jsonify({'error': 'Image trop lourde (max 4 Mo)'}), 400

    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f'{item_id}_{uuid.uuid4().hex[:8]}.{ext}'
    filepath = os.path.join(UPLOADS_DIR, filename)

    with open(filepath, 'wb') as f:
        f.write(data)

    image_path = f'/static/uploads/{filename}'
    update_menu_item(item_id, {'image_path': image_path})
    return jsonify({'message': 'Image uploadée', 'image_path': image_path})
