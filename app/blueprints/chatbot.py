"""
Chatbot Blueprint
Handles chatbot routes
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services.chatbot_service import chatbot_service

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__)

# Register routes
@chatbot_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle chatbot chat request"""
    try:
        # Check if request has JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400
        
        message = data.get('message', '').strip()
        conversation_history = data.get('history', [])  # Optional conversation history
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Check if chatbot service has API token
        if not chatbot_service.api_token:
            return jsonify({
                'success': False,
                'error': 'Chatbot API key not configured. Please contact administrator.'
            }), 500
        
        # Get chatbot response
        response = chatbot_service.chat(message, conversation_history)
        
        if response:
            return jsonify({
                'success': True,
                'response': response
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get chatbot response. Please check if GOOGLE_AI_API_KEY is set correctly.'
            }), 500
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error in chatbot route: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

