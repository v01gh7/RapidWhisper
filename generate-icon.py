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

        # Draw "RW" letters for RapidWhisper
        text = "RW"
        
        # Попробовать загрузить жирный шрифт для лучшей читаемости
        # Используем 85% от размера иконки для максимально крупных букв
        font = None
        initial_font_size = int(size * 0.85)
        
        # Приоритет: жирный шрифт для лучшей видимости
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
            "C:/Windows/Fonts/ariblk.ttf",   # Arial Black (еще жирнее)
            "C:/Windows/Fonts/impact.ttf",   # Impact (очень жирный)
            "C:/Windows/Fonts/arial.ttf",    # Arial обычный
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, initial_font_size)
                break
            except:
                continue
        
        # Если не удалось загрузить TrueType шрифт, используем default
        if font is None:
            print(f"  Warning: Using default font for {size}x{size}")
            font = ImageFont.load_default()
        
        # Получить размеры текста
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Если текст слишком большой, уменьшить шрифт
        max_width = int(size * 0.9)
        max_height = int(size * 0.9)
        
        if text_width > max_width or text_height > max_height:
            # Пересчитать размер шрифта
            scale = min(max_width / text_width, max_height / text_height)
            new_font_size = int(initial_font_size * scale)
            
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, new_font_size)
                    break
                except:
                    continue
            
            # Пересчитать размеры
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # Центрировать текст
        text_x = (size - text_width) // 2 - bbox[0]
        text_y = (size - text_height) // 2 - bbox[1]
        
        # Добавить легкую тень для контраста (только для больших иконок)
        if size >= 32:
            shadow_offset = max(1, size // 32)
            draw.text(
                (text_x + shadow_offset, text_y + shadow_offset), 
                text, 
                fill=(0, 0, 0, 100),  # Полупрозрачная черная тень
                font=font
            )
        
        # Нарисовать белый текст
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

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
    import os
    
    print("Generating RapidWhisper browser extension icons...")

    # Добавлены большие размеры для лучшего качества
    sizes = [16, 32, 48, 64, 128, 256]
    base_path = "public/icons"
    
    # Создать папку если её нет
    os.makedirs(base_path, exist_ok=True)
    print(f"✓ Directory {base_path} ready")

    for size in sizes:
        output_path = f"{base_path}/icon{size}.png"
        try:
            create_icon(size, output_path)
        except Exception as e:
            print(f"✗ Failed to create {output_path}: {e}")

    print("\nIcon generation complete!")

if __name__ == "__main__":
    main()
