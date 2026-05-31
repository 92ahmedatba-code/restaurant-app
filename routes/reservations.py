from flask import Blueprint, request, jsonify
from services import get_all_reservations, create_reservation, update_reservation_status, VALID_RES_STATUSES

reservations_bp = Blueprint('reservations', __name__)


@reservations_bp.route('/reservations', methods=['GET'])
def list_reservations():
    return jsonify(get_all_reservations())


@reservations_bp.route('/reservations', methods=['POST'])
def new_reservation():
    data = request.get_json(silent=True) or {}
    if not (data.get('customer_name') or '').strip():
        return jsonify({'error': 'Le nom est requis'}), 400
    if not (data.get('reservation_time') or '').strip():
        return jsonify({'error': "L'heure de réservation est requise"}), 400
    create_reservation(data)
    return jsonify({'message': 'Réservation créée avec succès'}), 201


@reservations_bp.route('/reservations/<int:res_id>/status', methods=['PATCH'])
def patch_reservation_status(res_id):
    data   = request.get_json(silent=True) or {}
    status = (data.get('status') or '').strip()
    if status not in VALID_RES_STATUSES:
        return jsonify({'error': f'Statut invalide. Valeurs: {", ".join(VALID_RES_STATUSES)}'}), 400
    try:
        update_reservation_status(res_id, status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'Statut mis à jour'})
