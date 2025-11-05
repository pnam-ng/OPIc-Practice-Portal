"""
Utility functions for generating PDF thumbnails
"""
import os
from PIL import Image
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    try:
        from pdf2image import convert_from_path
        HAS_PDF2IMAGE = True
    except ImportError:
        HAS_PDF2IMAGE = False


def generate_pdf_thumbnail(pdf_path, thumbnail_path, width=200, height=280):
    """
    Generate a thumbnail image from the first page of a PDF
    
    Args:
        pdf_path: Path to the PDF file
        thumbnail_path: Path where the thumbnail will be saved
        width: Thumbnail width in pixels (default: 200)
        height: Thumbnail height in pixels (default: 280)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(pdf_path):
        return False
    
    try:
        # Ensure thumbnail directory exists
        thumbnail_dir = os.path.dirname(thumbnail_path)
        if thumbnail_dir and not os.path.exists(thumbnail_dir):
            os.makedirs(thumbnail_dir, exist_ok=True)
        
        # Try PyMuPDF first (faster, lighter)
        if HAS_PYMUPDF:
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                # Get first page
                page = doc[0]
                # Render page to image (zoom factor for quality)
                zoom = 2.0  # Higher zoom = better quality
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Resize to thumbnail size while maintaining aspect ratio
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                img.save(thumbnail_path, 'PNG', optimize=True)
                doc.close()
                return True
            doc.close()
        
        # Fallback to pdf2image if PyMuPDF not available
        elif HAS_PDF2IMAGE:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
            if images:
                img = images[0]
                # Resize to thumbnail size while maintaining aspect ratio
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'PNG', optimize=True)
                return True
        
        return False
        
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_thumbnail_path(filename, base_dir):
    """
    Get the thumbnail path for a PDF filename
    
    Args:
        filename: PDF filename (e.g., 'example.pdf')
        base_dir: Base directory for storing thumbnails
    
    Returns:
        str: Thumbnail path
    """
    # Create thumbnail directory
    thumbnail_dir = os.path.join(base_dir, 'static', 'thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    # Convert filename to thumbnail filename
    thumbnail_filename = os.path.splitext(filename)[0] + '_thumb.png'
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
    
    return thumbnail_path




