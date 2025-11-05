"""
Main Blueprint
Handles main application routes
"""

from flask import Blueprint, send_from_directory
from flask_login import login_required
from app.controllers import MainController
import os

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

@main_bp.route('/chatbot')
@login_required
def chatbot():
    return main_controller.chatbot()

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

@main_bp.route('/tips')
@login_required
def tips():
    return main_controller.tips()

@main_bp.route('/files/<path:filename>')
@login_required
def serve_file(filename):
    """Serve PDF files from the files directory"""
    import os
    from flask import abort, current_app, request
    
    # Security check: only allow PDF files
    if not filename.endswith('.pdf'):
        current_app.logger.warning(f"Attempted access to non-PDF file: {filename}")
        abort(403)
    
    # Get the project root directory (same level as app.py)
    # This file is at: app/blueprints/main.py
    # We need: project_root/files/filename
    current_file = os.path.abspath(__file__)
    # Go up: app/blueprints -> app -> project_root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    files_dir = os.path.join(base_dir, 'files')
    
    # Normalize the path to handle Windows/Unix differences
    files_dir = os.path.normpath(files_dir)
    
    # Prevent directory traversal attacks - only allow filename, not path
    safe_filename = os.path.basename(filename)
    
    # Build file path
    file_path = os.path.join(files_dir, safe_filename)
    file_path = os.path.normpath(file_path)
    
    # Verify file is within files directory (security check)
    if not file_path.startswith(os.path.normpath(files_dir)):
        current_app.logger.warning(f"Directory traversal attempt: {filename}")
        abort(403)
    
    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        current_app.logger.error(f"PDF file not found: {file_path}")
        abort(404)
    
    try:
        # Determine if this is a download request
        download = request.args.get('download', 'false').lower() == 'true'
        
        # Serve the file
        response = send_from_directory(files_dir, safe_filename, as_attachment=download)
        
        # Set proper headers
        response.headers['Content-Type'] = 'application/pdf'
        if download:
            response.headers['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
        else:
            response.headers['Content-Disposition'] = f'inline; filename="{safe_filename}"'
        
        # Allow caching
        response.headers['Cache-Control'] = 'public, max-age=3600'
        
        return response
    except Exception as e:
        current_app.logger.error(f"Error serving PDF file {filename}: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        abort(500)


@main_bp.route('/files/preview/<path:filename>')
@login_required
def file_preview(filename):
    """Dynamically render the first page of a PDF as a PNG preview (no storage)."""
    import io
    from flask import abort, current_app, Response
    
    # Security: only allow PDFs
    if not filename.endswith('.pdf'):
        abort(403)
    
    # Resolve files directory
    current_file = os.path.abspath(__file__)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    files_dir = os.path.join(base_dir, 'files')
    files_dir = os.path.normpath(files_dir)
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(files_dir, safe_filename)
    file_path = os.path.normpath(file_path)
    if not file_path.startswith(os.path.normpath(files_dir)):
        abort(403)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        abort(404)
    
    # Try to generate preview using PyMuPDF
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        if len(doc) == 0:
            doc.close()
            abort(500)
        page = doc[0]
        zoom = 1.5
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img_bytes = pix.tobytes("png")
        doc.close()
        
        # Serve PNG with caching
        resp = Response(img_bytes, mimetype='image/png')
        resp.headers['Cache-Control'] = 'public, max-age=3600'
        return resp
    except Exception as e:
        current_app.logger.error(f"Failed to render PDF preview for {filename}: {e}")
        abort(500)

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

