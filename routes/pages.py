from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    return render_template('index.html')


@pages_bp.route('/admin')
def admin():
    return render_template('admin.html')


@pages_bp.route('/qr')
def qr_page():
    return render_template('qr.html')
