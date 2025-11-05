"""
Generate favicon matching Font Awesome fa-microphone-alt icon style
White icon on brand blue background
"""
from PIL import Image, ImageDraw
import os

def create_microphone_icon(size):
    """Create a microphone icon matching Font Awesome fa-microphone-alt style"""
    # Brand blue color (same as navbar)
    brand_blue = (13, 110, 253)  # #0d6efd
    white = (255, 255, 255)
    
    # Create image with brand blue background
    img = Image.new('RGB', (size, size), brand_blue)
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions based on size
    # Microphone takes up about 60% of canvas height
    mic_height = size * 0.6
    mic_width = mic_height * 0.4  # Microphone aspect ratio
    
    # Center the microphone
    center_x = size / 2
    center_y = size / 2
    
    # Microphone capsule (top part)
    capsule_top = (size * 0.15)
    capsule_height = mic_height * 0.5
    capsule_width = mic_width
    
    capsule_left = center_x - capsule_width / 2
    capsule_right = center_x + capsule_width / 2
    capsule_bottom = capsule_top + capsule_height
    
    # Draw rounded rectangle for microphone capsule
    draw.rounded_rectangle(
        [capsule_left, capsule_top, capsule_right, capsule_bottom],
        radius=capsule_width / 2,
        fill=white
    )
    
    # Draw the arc/bracket below microphone (classic mic stand)
    arc_width = mic_width * 1.8
    arc_height = mic_height * 0.35
    arc_top = capsule_bottom + (size * 0.05)
    arc_bottom = arc_top + arc_height
    
    # Draw U-shaped arc
    arc_left = center_x - arc_width / 2
    arc_right = center_x + arc_width / 2
    
    line_width = max(2, int(size / 20))
    
    # Draw the U-shape (arc on sides and bottom)
    draw.arc(
        [arc_left, arc_top, arc_right, arc_bottom],
        start=180, end=0,
        fill=white,
        width=line_width
    )
    
    # Draw vertical line from center of arc down
    line_top = arc_top + (arc_height / 2)
    line_bottom = size * 0.85
    
    draw.line(
        [center_x, line_top, center_x, line_bottom],
        fill=white,
        width=line_width
    )
    
    # Draw base (horizontal line at bottom)
    base_width = mic_width * 1.4
    base_y = size * 0.88
    
    draw.line(
        [center_x - base_width/2, base_y, center_x + base_width/2, base_y],
        fill=white,
        width=line_width + 1
    )
    
    # Add detail lines on capsule if size is large enough
    if size >= 32:
        detail_count = 3 if size >= 64 else 2
        detail_spacing = capsule_height / (detail_count + 1)
        
        for i in range(1, detail_count + 1):
            y = capsule_top + (detail_spacing * i)
            detail_width = capsule_width * 0.7
            
            draw.line(
                [center_x - detail_width/2, y, center_x + detail_width/2, y],
                fill=brand_blue,
                width=max(1, int(size / 40))
            )
    
    return img

def create_all_favicons():
    """Create all favicon sizes"""
    print("Generating Font Awesome style favicon...")
    
    # Standard sizes
    sizes = [16, 32, 48, 64, 72, 96, 128, 144, 192, 256]
    
    # Create directory
    os.makedirs('static/icons', exist_ok=True)
    
    # Generate PNG icons
    for size in sizes:
        img = create_microphone_icon(size)
        img.save(f'static/icons/icon-{size}x{size}.png', 'PNG')
        print(f'✓ Created icon-{size}x{size}.png')
    
    # Create favicon.ico (multi-size)
    ico_sizes = [16, 32, 48]
    images = []
    
    for size in ico_sizes:
        img = create_microphone_icon(size)
        images.append(img)
    
    # Save as favicon.ico
    images[0].save(
        'static/favicon.ico',
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print('✓ Created favicon.ico')
    
    print('\n✅ All Font Awesome style favicons generated successfully!')
    print('   Style: fa-microphone-alt')
    print('   Colors: White on Brand Blue (#0d6efd)')

if __name__ == '__main__':
    create_all_favicons()

































