"""
Generate beautiful PWA icons with proper styling:
- Blue background (#0d6efd)
- White microphone icon centered
- Proper padding (20%)
- Optional rounded corners for modern look
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_pretty_icon(size, source_img, output_path):
    """Create a single pretty icon with background and padding"""
    
    # Create new image with white background
    bg_color = (255, 255, 255)  # White background
    icon = Image.new('RGBA', (size, size), bg_color + (255,))
    
    # Calculate padding (20% on each side, so icon is 60% of total size)
    padding = int(size * 0.2)
    icon_size = size - (padding * 2)
    
    # Resize source image to fit with padding (keep original blue color)
    resized_source = source_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    
    # Ensure we have an RGBA image
    if resized_source.mode != 'RGBA':
        resized_source = resized_source.convert('RGBA')
    
    # Center and paste the blue microphone icon onto white background
    icon.paste(resized_source, (padding, padding), resized_source)
    
    # Add subtle rounded corners for sizes 128+
    if size >= 128:
        # Create a mask with rounded corners
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        
        # Corner radius proportional to size
        corner_radius = int(size * 0.15)  # 15% of size
        
        # Draw rounded rectangle
        draw.rounded_rectangle(
            [(0, 0), (size-1, size-1)],
            radius=corner_radius,
            fill=255
        )
        
        # Apply mask with smooth edges
        output = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        output.paste(icon, (0, 0))
        output.putalpha(mask)
        
        return output
    
    return icon

def generate_pretty_icons():
    """Generate all pretty icon sizes"""
    
    # Source image
    source_path = os.path.join('static', 'microphone.png')
    if not os.path.exists(source_path):
        print(f"✗ Source file not found: {source_path}")
        return False
    
    # Load source image
    try:
        source_img = Image.open(source_path)
        print(f"✓ Loaded source image: {source_img.size[0]}x{source_img.size[1]}")
    except Exception as e:
        print(f"✗ Error loading image: {e}")
        return False
    
    # Icon sizes
    sizes = [16, 32, 48, 64, 72, 96, 128, 144, 192, 256, 512]
    
    # Create icons directory
    icons_dir = os.path.join('static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # Generate each size
    for size in sizes:
        try:
            # Create pretty icon
            pretty_icon = create_pretty_icon(size, source_img, None)
            
            # Save as PNG
            output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
            pretty_icon.save(output_path, 'PNG', optimize=True)
            
            print(f"✓ Generated: icon-{size}x{size}.png (with blue background & padding)")
        except Exception as e:
            print(f"✗ Error generating {size}x{size}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✓ All pretty PWA icons generated!")
    print("✓ Features:")
    print("  - White/clean background")
    print("  - Original blue microphone icon (centered)")
    print("  - 20% padding for professional look")
    print("  - Rounded corners on larger icons (128px+)")
    print(f"✓ Icons saved to: {icons_dir}/")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Generating Pretty PWA Icons")
    print("=" * 60)
    print()
    success = generate_pretty_icons()
    sys.exit(0 if success else 1)

