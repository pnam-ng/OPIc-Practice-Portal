"""
Vocabulary Blueprint - REST API for vocabulary feature
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

vocabulary_bp = Blueprint('vocabulary', __name__)


def get_vocab_service():
    """Lazy import to avoid circular import"""
    from app.services.vocabulary_service import VocabularyService
    return VocabularyService()


# ==================== Public Endpoints ====================

@vocabulary_bp.route('/', methods=['GET'])
def get_vocabulary():
    """Get vocabulary list with optional filters"""
    topic = request.args.get('topic')
    pos = request.args.get('pos')  # part of speech
    search = request.args.get('search', request.args.get('q'))
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    words = get_vocab_service().get_vocabulary(
        topic=topic, pos=pos, search=search, 
        limit=limit, offset=offset
    )
    
    return jsonify({
        'success': True,
        'data': [w.to_dict() for w in words],
        'count': len(words)
    })


@vocabulary_bp.route('/<int:vocab_id>', methods=['GET'])
def get_word(vocab_id):
    """Get single vocabulary word details"""
    word = get_vocab_service().get_word_by_id(vocab_id)
    if not word:
        return jsonify({'success': False, 'error': 'Word not found'}), 404
    
    return jsonify({
        'success': True,
        'data': word.to_dict()
    })


@vocabulary_bp.route('/search', methods=['GET'])
def search_vocabulary():
    """Search vocabulary"""
    query = request.args.get('q', '')
    limit = min(int(request.args.get('limit', 20)), 50)
    
    if not query or len(query) < 2:
        return jsonify({'success': False, 'error': 'Query too short'}), 400
    
    words = get_vocab_service().search_vocabulary(query, limit)
    
    return jsonify({
        'success': True,
        'data': [w.to_dict() for w in words],
        'count': len(words)
    })


@vocabulary_bp.route('/lookup/<word>', methods=['GET'])
def lookup_word(word):
    """Look up word from Free Dictionary API"""
    result = get_vocab_service().lookup_word(word)
    if not result:
        return jsonify({'success': False, 'error': 'Word not found'}), 404
    
    return jsonify({
        'success': True,
        'data': result
    })


@vocabulary_bp.route('/word-of-day', methods=['GET'])
def get_word_of_day():
    """Get today's word of the day"""
    wod = get_vocab_service().get_word_of_day()
    if not wod:
        return jsonify({'success': False, 'error': 'No word of day'}), 404
    
    return jsonify({
        'success': True,
        'data': wod
    })


@vocabulary_bp.route('/topics', methods=['GET'])
def get_topics():
    """Get list of vocabulary topics"""
    topics = get_vocab_service().get_topics()
    return jsonify({
        'success': True,
        'data': topics
    })


@vocabulary_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get vocabulary statistics"""
    user_id = current_user.id if current_user.is_authenticated else None
    stats = get_vocab_service().get_stats(user_id)
    return jsonify({
        'success': True,
        'data': stats
    })


# ==================== User Vocabulary Endpoints ====================

@vocabulary_bp.route('/user', methods=['GET'])
@login_required
def get_user_vocabulary():
    """Get current user's vocabulary list"""
    status = request.args.get('status')
    favorites_only = request.args.get('favorites') == 'true'
    
    user_vocab = get_vocab_service().get_user_vocabulary(
        current_user.id, status=status, favorites_only=favorites_only
    )
    
    return jsonify({
        'success': True,
        'data': [uv.to_dict() for uv in user_vocab],
        'count': len(user_vocab)
    })


@vocabulary_bp.route('/user', methods=['POST'])
@login_required
def add_to_user_vocabulary():
    """Add word to user's vocabulary list"""
    data = request.get_json()
    vocab_id = data.get('vocabulary_id')
    
    if not vocab_id:
        return jsonify({'success': False, 'error': 'vocabulary_id required'}), 400
    
    user_vocab = get_vocab_service().add_to_user_vocabulary(current_user.id, vocab_id)
    
    return jsonify({
        'success': True,
        'data': user_vocab.to_dict()
    })


@vocabulary_bp.route('/user/<int:vocab_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(vocab_id):
    """Toggle favorite status for a word"""
    is_favorite = get_vocab_service().toggle_favorite(current_user.id, vocab_id)
    
    return jsonify({
        'success': True,
        'is_favorite': is_favorite
    })


# ==================== Review Endpoints ====================

@vocabulary_bp.route('/review', methods=['GET'])
@login_required
def get_due_reviews():
    """Get words due for review"""
    limit = min(int(request.args.get('limit', 10)), 20)
    
    reviews = get_vocab_service().get_due_reviews(current_user.id, limit)
    
    return jsonify({
        'success': True,
        'data': [r.to_dict() for r in reviews],
        'count': len(reviews)
    })


@vocabulary_bp.route('/review', methods=['POST'])
@login_required
def record_review():
    """Record review result"""
    data = request.get_json()
    vocab_id = data.get('vocabulary_id')
    correct = data.get('correct', False)
    
    if not vocab_id:
        return jsonify({'success': False, 'error': 'vocabulary_id required'}), 400
    
    user_vocab = get_vocab_service().record_review(current_user.id, vocab_id, correct)
    
    return jsonify({
        'success': True,
        'data': user_vocab.to_dict()
    })
