"""
Authentication Blueprint
Handles user authentication routes
"""

from flask import Blueprint
from app.controllers import AuthController

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize controller
auth_controller = AuthController()

# Register routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return auth_controller.login()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return auth_controller.register()

@auth_bp.route('/logout')
def logout():
    return auth_controller.logout()

