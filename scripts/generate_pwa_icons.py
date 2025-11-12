"""
Generate all PWA icon sizes from the source microphone.png
"""
import os
import sys
from PIL import Image

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def generate_icons():
    """Generate all icon sizes from microphone.png"""
    
    # Source image
    source_path = os.path.join('static', 'microphone.png')
    if not os.path.exists(source_path):
        print(f"✗ Source file not found: {source_path}")
        return False
    
    # Load source image
    try:
        img = Image.open(source_path)
        print(f"✓ Loaded source image: {img.size[0]}x{img.size[1]}")
    except Exception as e:
        print(f"✗ Error loading image: {e}")
        return False
    
    # Icon sizes needed for PWA
    sizes = [16, 32, 48, 64, 72, 96, 128, 144, 192, 256, 512]
    
    # Create icons directory if it doesn't exist
    icons_dir = os.path.join('static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # Generate each size
    for size in sizes:
        try:
            # Resize image
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save as PNG
            output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
            resized.save(output_path, 'PNG', optimize=True)
            print(f"✓ Generated: icon-{size}x{size}.png")
        except Exception as e:
            print(f"✗ Error generating {size}x{size}: {e}")
    
    print("\n✓ All PWA icons generated successfully!")
    print(f"✓ Icons saved to: {icons_dir}/")
    return True

if __name__ == '__main__':
    print("Generating PWA icons from microphone.png...\n")
    success = generate_icons()
    sys.exit(0 if success else 1)








































