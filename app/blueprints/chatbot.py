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
        # Refresh API token from environment in case it wasn't loaded at startup
        if not chatbot_service.api_token:
            import os
            chatbot_service.api_token = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
            
            # Also try to get from Flask config
            if not chatbot_service.api_token:
                try:
                    chatbot_service.api_token = current_app.config.get("GOOGLE_AI_API_KEY") or current_app.config.get("GEMINI_API_KEY")
                except:
                    pass
        
        if not chatbot_service.api_token:
            return jsonify({
                'success': False,
                'error': 'Chatbot API key not configured. Please contact administrator.'
            }), 500
        
        # Get chatbot response with timeout protection
        from flask import current_app
        current_app.logger.info(f"Chatbot request received: {message[:50]}...")
        
        response = chatbot_service.chat(message, conversation_history)
        
        if response:
            current_app.logger.info(f"Chatbot response generated successfully: {len(response)} chars")
            return jsonify({
                'success': True,
                'response': response
            })
        else:
            current_app.logger.warning("Chatbot service returned None - API may be rate limited or unavailable")
            return jsonify({
                'success': False,
                'error': 'Failed to get chatbot response. The AI service may be temporarily unavailable. Please try again in a moment.'
            }), 500
        
    except TimeoutError as e:
        from flask import current_app
        current_app.logger.error(f"Chatbot request timed out: {e}")
        return jsonify({
            'success': False,
            'error': 'Request timed out. The AI service is taking too long to respond. Please try again with a shorter question.'
        }), 504
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error in chatbot route: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

