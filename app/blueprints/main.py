"""
Main Blueprint
Handles main application routes
"""

from flask import Blueprint
from flask_login import login_required
from app.controllers import MainController

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize controller
main_controller = MainController()

# Register routes
@main_bp.route('/')
def index():
    return main_controller.index()

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return main_controller.dashboard()

@main_bp.route('/test')
@login_required
def test_mode():
    return main_controller.test_mode()

@main_bp.route('/practice')
@login_required
def practice_mode():
    return main_controller.practice_mode()

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return main_controller.profile()

@main_bp.route('/pwa-guide')
def pwa_guide():
    return main_controller.pwa_guide()

@main_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    return main_controller.change_password()

@main_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    return main_controller.upload_avatar()

@main_bp.route('/history')
@login_required
def history():
    return main_controller.history()

