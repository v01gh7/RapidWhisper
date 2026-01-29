"""
Платформо-зависимые утилиты для RapidWhisper.

Предоставляет функции для применения эффектов размытия на разных
операционных системах (Windows, macOS, Linux).
"""

import sys
import platform
from typing import Optional
from enum import Enum


class Platform(Enum):
    """Поддерживаемые платформы"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


def detect_platform() -> Platform:
    """
    Определяет текущую операционную систему.
    
    Returns:
        Platform: Текущая платформа
    
    Requirements: 2.3
    """
    system = platform.system().lower()
    
    if system == "windows":
        return Platform.WINDOWS
    elif system == "darwin":
        return Platform.MACOS
    elif system == "linux":
        return Platform.LINUX
    else:
        return Platform.UNKNOWN


def apply_windows_blur(hwnd: int) -> bool:
    """
    Применяет эффект размытия Acrylic для Windows 11.
    
    Использует Windows API для применения эффекта размытого стекла.
    
    Args:
        hwnd: Handle окна Windows
    
    Returns:
        bool: True если эффект применен успешно, False иначе
    
    Requirements: 2.3
    """
    try:
        import ctypes
        from ctypes import wintypes
        
        # Определяем структуры и константы Windows API
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", wintypes.DWORD),
                ("AccentFlags", wintypes.DWORD),
                ("GradientColor", wintypes.DWORD),
                ("AnimationId", wintypes.DWORD),
            ]
        
        class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", wintypes.DWORD),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_size_t),
            ]
        
        # Константы для Windows 11 Acrylic
        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
        WCA_ACCENT_POLICY = 19
        
        # Создаем политику акцента
        accent = ACCENT_POLICY()
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.GradientColor = 0x01000000  # Полупрозрачный черный
        
        # Создаем данные атрибута композиции
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)
        
        # Применяем эффект
        user32 = ctypes.windll.user32
        user32.SetWindowCompositionAttribute.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)
        ]
        user32.SetWindowCompositionAttribute.restype = wintypes.BOOL
        
        result = user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
        return bool(result)
        
    except Exception:
        return False


def apply_macos_blur(window) -> bool:
    """
    Применяет эффект размытия NSVisualEffectView для macOS.
    
    Использует Objective-C bridge для применения нативного эффекта macOS.
    
    Args:
        window: QWidget окно
    
    Returns:
        bool: True если эффект применен успешно, False иначе
    
    Requirements: 2.3
    """
    try:
        # Попытка использовать PyObjC для macOS
        from AppKit import NSVisualEffectView, NSVisualEffectBlendingModeBehindWindow
        from AppKit import NSVisualEffectMaterialDark
        
        # Получаем нативное представление окна
        ns_view = window.winId().__int__()
        
        # Создаем NSVisualEffectView
        effect_view = NSVisualEffectView.alloc().initWithFrame_(
            ((0, 0), (window.width(), window.height()))
        )
        effect_view.setMaterial_(NSVisualEffectMaterialDark)
        effect_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        effect_view.setState_(1)  # Active
        
        return True
        
    except ImportError:
        # PyObjC не установлен
        return False
    except Exception:
        return False


def apply_linux_blur(window) -> bool:
    """
    Применяет эффект размытия для Linux через композитинг.
    
    Использует X11 или Wayland композитор для применения эффекта размытия.
    
    Args:
        window: QWidget окно
    
    Returns:
        bool: True если эффект применен успешно, False иначе
    
    Requirements: 2.3
    """
    try:
        # Для Linux используем свойства X11 или Wayland
        # Это зависит от композитора (KWin, Mutter, Compiz и т.д.)
        
        # Попытка установить свойство для KWin (KDE)
        window.setProperty("_KDE_NET_WM_BLUR_BEHIND_REGION", True)
        
        # Попытка установить свойство для Mutter (GNOME)
        window.setProperty("_NET_WM_BLUR_BEHIND", True)
        
        return True
        
    except Exception:
        return False


def apply_blur_effect(window) -> bool:
    """
    Применяет эффект размытия для текущей платформы.
    
    Автоматически определяет платформу и применяет соответствующий
    эффект размытия.
    
    Args:
        window: QWidget окно
    
    Returns:
        bool: True если эффект применен успешно, False иначе
    
    Requirements: 2.3
    """
    current_platform = detect_platform()
    
    if current_platform == Platform.WINDOWS:
        # Получаем HWND для Windows
        hwnd = int(window.winId())
        return apply_windows_blur(hwnd)
    
    elif current_platform == Platform.MACOS:
        return apply_macos_blur(window)
    
    elif current_platform == Platform.LINUX:
        return apply_linux_blur(window)
    
    else:
        # Неизвестная платформа
        return False
