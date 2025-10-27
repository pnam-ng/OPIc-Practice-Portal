"""
Test Mode Blueprint
Handles test mode routes
"""

from flask import Blueprint
from flask_login import login_required
from app.controllers import TestModeController

# Create blueprint
test_mode_bp = Blueprint('test_mode', __name__)

# Initialize controller
test_mode_controller = TestModeController()

# Register routes
@test_mode_bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    return test_mode_controller.survey()

@test_mode_bp.route('/questions')
@login_required
def questions():
    return test_mode_controller.questions()

@test_mode_bp.route('/record/<int:question_id>', methods=['POST'])
@login_required
def record_response(question_id):
    return test_mode_controller.record_response(question_id)

@test_mode_bp.route('/finish')
@login_required
def finish_test():
    return test_mode_controller.finish_test()
