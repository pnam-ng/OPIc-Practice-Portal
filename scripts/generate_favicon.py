"""
Generate favicon and app icons for OPIc Practice Portal
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Create an icon with a microphone symbol"""
    # Create image with blue background (OPIc brand color)
    img = Image.new('RGB', (size, size), color='#0d6efd')
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions for the microphone
    padding = size // 6
    
    # Draw microphone shape
    # Microphone body (rounded rectangle)
    mic_width = size // 3
    mic_height = size // 2
    mic_x = (size - mic_width) // 2
    mic_y = size // 5
    
    # Draw white microphone
    draw.rounded_rectangle(
        [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height],
        radius=mic_width // 3,
        fill='white'
    )
    
    # Draw microphone stand (line)
    stand_x = size // 2
    stand_y_start = mic_y + mic_height
    stand_y_end = size - padding
    draw.line(
        [(stand_x, stand_y_start), (stand_x, stand_y_end)],
        fill='white',
        width=max(2, size // 16)
    )
    
    # Draw base (horizontal line)
    base_width = size // 3
    base_y = stand_y_end
    draw.line(
        [(stand_x - base_width // 2, base_y), (stand_x + base_width // 2, base_y)],
        fill='white',
        width=max(2, size // 16)
    )
    
    return img

def main():
    # Define icon sizes
    sizes = [16, 32, 72, 96, 128, 144, 192, 512]
    
    # Ensure icons directory exists
    icons_dir = os.path.join('static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    print("Generating OPIc Practice Portal icons...")
    
    # Generate PNG icons
    for size in sizes:
        icon = create_icon(size, None)
        output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        icon.save(output_path, 'PNG')
        print(f"✓ Created {output_path}")
    
    # Generate favicon.ico (multi-resolution)
    favicon_sizes = [16, 32, 48]
    favicon_images = [create_icon(size, None) for size in favicon_sizes]
    
    favicon_path = os.path.join('static', 'favicon.ico')
    favicon_images[0].save(
        favicon_path,
        format='ICO',
        sizes=[(size, size) for size in favicon_sizes],
        append_images=favicon_images[1:]
    )
    print(f"✓ Created {favicon_path}")
    
    print("\n✅ All icons generated successfully!")
    print("\nGenerated files:")
    print(f"  - favicon.ico (16x16, 32x32, 48x48)")
    for size in sizes:
        print(f"  - icon-{size}x{size}.png")

if __name__ == '__main__':
    main()
































