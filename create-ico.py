#!/usr/bin/env python
"""
Create .ico file from PNG icons for Windows.
"""

from PIL import Image

def create_ico():
    """Create .ico file from PNG icons."""
    print("Creating RapidWhisper.ico...")
    
    # Загрузить PNG иконки - все размеры для лучшего качества
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        try:
            img = Image.open(f"public/icons/icon{size}.png")
            images.append(img)
            print(f"✓ Loaded icon{size}.png")
        except Exception as e:
            print(f"✗ Failed to load icon{size}.png: {e}")
            return
    
    # Сохранить как .ico
    try:
        images[0].save(
            "public/RapidWhisper.ico",
            format='ICO',
            sizes=[(img.width, img.height) for img in images]
        )
        print("✓ Created public/RapidWhisper.ico")
    except Exception as e:
        print(f"✗ Failed to create .ico: {e}")

if __name__ == "__main__":
    create_ico()
