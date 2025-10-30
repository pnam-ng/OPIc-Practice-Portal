"""
Practice Mode Blueprint
Handles practice mode routes
"""

from flask import Blueprint
from flask_login import login_required
from app.controllers import PracticeModeController

# Create blueprint
practice_mode_bp = Blueprint('practice_mode', __name__)

# Initialize controller
practice_mode_controller = PracticeModeController()

# Register routes
@practice_mode_bp.route('/')
@login_required
def index():
    return practice_mode_controller.index()

@practice_mode_bp.route('/start', methods=['POST'])
@login_required
def start_practice():
    return practice_mode_controller.start_practice()

@practice_mode_bp.route('/question/<int:question_id>')
@login_required
def question(question_id):
    return practice_mode_controller.question(question_id)

@practice_mode_bp.route('/record_practice_response/<int:question_id>', methods=['POST'])
@login_required
def record_practice_response(question_id):
    return practice_mode_controller.record_practice_response(question_id)

@practice_mode_bp.route('/topics/<level>')
@login_required
def get_topics_by_level(level):
    return practice_mode_controller.get_topics_by_level(level)

@practice_mode_bp.route('/congratulations')
@login_required
def congratulations():
    return practice_mode_controller.congratulations()
