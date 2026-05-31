from flask import Blueprint, jsonify
from services import get_stats

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats', methods=['GET'])
def dashboard_stats():
    try:
        return jsonify(get_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
