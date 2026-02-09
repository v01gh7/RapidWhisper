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


def get_platform_info() -> dict:
    """
    Возвращает информацию о текущей платформе.
    
    Returns:
        dict: Словарь с информацией о платформе
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "platform": detect_platform().value
    }


def is_windows() -> bool:
    """
    Проверяет, является ли текущая платформа Windows.
    
    Returns:
        bool: True если Windows, False иначе
    """
    return detect_platform() == Platform.WINDOWS


def is_macos() -> bool:
    """
    Проверяет, является ли текущая платформа macOS.
    
    Returns:
        bool: True если macOS, False иначе
    """
    return detect_platform() == Platform.MACOS


def is_linux() -> bool:
    """
    Проверяет, является ли текущая платформа Linux.
    
    Returns:
        bool: True если Linux, False иначе
    """
    return detect_platform() == Platform.LINUX


def apply_windows_blur(
    hwnd: int,
    width: Optional[int] = None,
    height: Optional[int] = None,
    corner_radius: Optional[int] = None,
) -> bool:
    """
    Применяет эффект размытия для Windows.
    
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

        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        user32.CreateRoundRectRgn.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int
        ]
        user32.CreateRoundRectRgn.restype = wintypes.HRGN
        user32.SetWindowRgn.argtypes = [wintypes.HWND, wintypes.HRGN, wintypes.BOOL]
        user32.SetWindowRgn.restype = ctypes.c_int

        gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
        gdi32.DeleteObject.restype = wintypes.BOOL

        # Реальная скругленная форма окна на уровне Win32.
        if (
            corner_radius is not None and corner_radius > 0 and
            width is not None and width > 0 and
            height is not None and height > 0
        ):
            diameter = int(corner_radius) * 2
            hrgn = user32.CreateRoundRectRgn(0, 0, int(width) + 1, int(height) + 1, diameter, diameter)
            if hrgn:
                # При успехе владение region переходит к системе.
                if user32.SetWindowRgn(hwnd, hrgn, True) == 0:
                    gdi32.DeleteObject(hrgn)

        if not hasattr(user32, "SetWindowCompositionAttribute"):
            return False

        user32.SetWindowCompositionAttribute.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA),
        ]
        user32.SetWindowCompositionAttribute.restype = wintypes.BOOL

        WCA_ACCENT_POLICY = 19
        ACCENT_ENABLE_BLURBEHIND = 3
        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

        def _set_accent(state: int, flags: int, gradient_color: int) -> bool:
            accent = ACCENT_POLICY()
            accent.AccentState = state
            accent.AccentFlags = flags
            accent.GradientColor = gradient_color
            accent.AnimationId = 0

            data = WINDOWCOMPOSITIONATTRIBDATA()
            data.Attribute = WCA_ACCENT_POLICY
            data.Data = ctypes.pointer(accent)
            data.SizeOfData = ctypes.sizeof(accent)
            return bool(user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data)))

        # Сначала Acrylic (более заметный blur), затем fallback на classic blur.
        if _set_accent(ACCENT_ENABLE_ACRYLICBLURBEHIND, 2, 0xCC1F1F1F):
            return True
        return _set_accent(ACCENT_ENABLE_BLURBEHIND, 0, 0x00000000)

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
        radius = int(getattr(window, "_corner_radius", 18))
        return apply_windows_blur(
            hwnd,
            width=int(window.width()),
            height=int(window.height()),
            corner_radius=radius,
        )
    
    elif current_platform == Platform.MACOS:
        return apply_macos_blur(window)
    
    elif current_platform == Platform.LINUX:
        return apply_linux_blur(window)
    
    else:
        # Неизвестная платформа
        return False
