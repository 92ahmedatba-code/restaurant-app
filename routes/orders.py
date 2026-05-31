from flask import Blueprint, request, jsonify
from services import get_all_orders, create_order, update_order_status, VALID_ORDER_STATUSES

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/orders', methods=['GET'])
def list_orders():
    return jsonify(get_all_orders())


@orders_bp.route('/orders', methods=['POST'])
def new_order():
    data = request.get_json(silent=True) or {}
    if not (data.get('customer_name') or '').strip():
        return jsonify({'error': 'Le nom du client est requis'}), 400
    if not (data.get('items') or '').strip():
        return jsonify({'error': 'Les articles commandés sont requis'}), 400
    create_order(data)
    return jsonify({'message': 'Commande créée avec succès'}), 201


@orders_bp.route('/orders/<int:order_id>/status', methods=['PATCH'])
def patch_order_status(order_id):
    data   = request.get_json(silent=True) or {}
    status = (data.get('status') or '').strip()
    if status not in VALID_ORDER_STATUSES:
        return jsonify({'error': f'Statut invalide. Valeurs: {", ".join(VALID_ORDER_STATUSES)}'}), 400
    try:
        update_order_status(order_id, status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'Statut mis à jour'})
