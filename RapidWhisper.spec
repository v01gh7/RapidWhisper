# -*- mode: python ; coding: utf-8 -*-

# RapidWhisper PyInstaller Configuration - WINDOWS
# 
# ВАЖНО: Этот spec файл НЕ включает config.jsonc и secrets.json!
# Настройки сохраняются в %APPDATA%/RapidWhisper/
#
# build.bat автоматически:
# 1. Сохраняет ваши config.jsonc и secrets.json
# 2. Очищает старую сборку
# 3. Собирает чистый .exe без конфигов
# 4. Восстанавливает ваши конфиги для разработки
#
# Включается в сборку:
# - Иконки для UI (public/icons/)
# - Промпты форматирования (config/prompts/)
# - Основная иконка приложения (public/RapidWhisper.ico)
#
# Результат: Чистый .exe файл, настройки в AppData

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Основная иконка приложения
        ('public/RapidWhisper.ico', 'public'),
        
        # Иконки для UI (окна настроек, кнопки и т.д.)
        ('public/icons/*.svg', 'public/icons'),
        ('public/icons/*.png', 'public/icons'),
        
        # Промпты форматирования (обязательны для работы форматирования)
        ('config/prompts/*.txt', 'config/prompts'),
        
        # Примеры конфигов (для создания дефолтных при первом запуске)
        ('config.jsonc.example', '.'),
        ('secrets.json.example', '.'),
        
        # Переводы интерфейса (все языки)
        ('utils/translations/*.json', 'utils/translations'),
        
        # НЕ включаем config.jsonc и secrets.json - они создаются в AppData
        # НЕ включаем тестовые конфиги - они только для разработки
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtSvg',  # Для SVG иконок
        'pyaudio',
        'numpy',
        'keyboard',
        'pyperclip',
        'psutil',
        'openai',
        'tzdata',  # Для работы с временными зонами
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'PIL',
        'tkinter',
        'pytest',
        'hypothesis',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RapidWhisper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консоли для production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/RapidWhisper.ico',  # Иконка для .exe файла
)
