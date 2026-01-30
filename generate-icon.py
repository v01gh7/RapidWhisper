#!/usr/bin/env python
"""
Generate PNG icons for the RapidWhisper browser extension.
Creates simple icons with a grammar checker theme.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    has_pil = True
except ImportError:
    has_pil = False

def create_icon(size, output_path):
    """Create a simple icon for the browser extension."""
    if has_pil:
        # Use Pillow for better quality icons
        img = Image.new('RGBA', (size, size), (79, 70, 229, 255))  # Indigo background
        draw = ImageDraw.Draw(img)

        # Draw a simple "RW" letter for RapidWhisper
        margin = size // 8
        font_size = size - 2 * margin

        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fall back to default font
            font = ImageFont.load_default()

        # Draw "R" in white
        text_bbox = draw.textbbox((0, 0), "RW", font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - text_bbox[1]
        draw.text((text_x, text_y), "R", fill=(255, 255, 255, 255), font=font)

        img.save(output_path, 'PNG')
        print(f"✓ Created {output_path} ({size}x{size})")
    else:
        # Fallback: Create minimal valid PNG without Pillow
        import struct
        import zlib

        # Create a simple 1x1 PNG and scale it
        # PNG signature
        png_signature = b'\x89PNG\r\n\x1a\n'

        # IHDR chunk
        width = size
        height = size
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
        ihdr_chunk = create_chunk(b'IHDR', ihdr_data)

        # IDAT chunk - simple solid color (indigo: #4F46E5)
        # Create image data
        pixels = b''
        for y in range(height):
            row = b'\x00'  # Filter type 0 (none)
            for x in range(width):
                # RGBA: indigo color
                row += b'\x4F\x46\xE5\xFF'
            pixels += row

        compressed = zlib.compress(pixels, 9)
        idat_chunk = create_chunk(b'IDAT', compressed)

        # IEND chunk
        iend_chunk = create_chunk(b'IEND', b'')

        # Write PNG file
        with open(output_path, 'wb') as f:
            f.write(png_signature + ihdr_chunk + idat_chunk + iend_chunk)

        print(f"✓ Created {output_path} ({size}x{size}) - minimal PNG")

def create_chunk(chunk_type, data):
    """Create a PNG chunk."""
    import struct
    import zlib

    length = struct.pack('>I', len(data))
    crc = zlib.crc32(chunk_type + data) & 0xffffffff
    crc_bytes = struct.pack('>I', crc)

    return length + chunk_type + data + crc_bytes

def main():
    """Generate all icon sizes."""
    print("Generating RapidWhisper browser extension icons...")

    sizes = [16, 48, 128]
    base_path = "public/icons"

    for size in sizes:
        output_path = f"{base_path}/icon{size}.png"
        try:
            create_icon(size, output_path)
        except Exception as e:
            print(f"✗ Failed to create {output_path}: {e}")

    print("\nIcon generation complete!")

if __name__ == "__main__":
    main()
