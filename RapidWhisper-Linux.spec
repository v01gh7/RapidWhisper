# -*- mode: python ; coding: utf-8 -*-

# RapidWhisper PyInstaller Configuration - Linux
# 
# Настройки сохраняются в ~/.config/RapidWhisper/
#
# Включается в сборку:
# - Иконки для UI (public/icons/)
# - Промпты форматирования (config/prompts/)
# - Переводы интерфейса (utils/translations/)
#
# Результат: Исполняемый файл для Linux

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
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
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtSvg',
        'pyaudio',
        'numpy',
        'keyboard',
        'pyperclip',
        'psutil',
        'openai',
        'tzdata',
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Linux не использует иконку в исполняемом файле
)
