"""
Модуль для обеспечения единственного экземпляра приложения.

Использует файл блокировки для предотвращения запуска нескольких экземпляров.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
import psutil


class SingleInstance:
    """
    Класс для обеспечения единственного экземпляра приложения.
    
    Создает файл блокировки при запуске и удаляет его при завершении.
    Если файл блокировки уже существует, проверяет что процесс действительно запущен.
    """
    
    def __init__(self, app_name: str = "RapidWhisper"):
        """
        Инициализирует проверку единственного экземпляра.
        
        Args:
            app_name: Имя приложения для файла блокировки
        """
        self.app_name = app_name
        self.lock_file: Optional[Path] = None
        self.lock_handle = None
        
        # Путь к файлу блокировки в temp директории
        temp_dir = Path(tempfile.gettempdir())
        self.lock_file = temp_dir / f"{app_name}.lock"
    
    def is_already_running(self) -> bool:
        """
        Проверяет, запущен ли уже экземпляр приложения.
        
        Returns:
            True если приложение уже запущено, False иначе
        """
        if not self.lock_file.exists():
            return False
        
        # Прочитать PID из файла блокировки
        try:
            with open(self.lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Проверить что процесс с таким PID существует
            if psutil.pid_exists(pid):
                try:
                    # Проверить что процесс действительно существует и доступен
                    process = psutil.Process(pid)
                    # Если процесс существует и доступен, считаем что приложение запущено
                    return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Процесс не существует или недоступен
                    pass
            
            # Процесс не существует - удалить старый lock файл
            self.lock_file.unlink(missing_ok=True)
            return False
            
        except (ValueError, FileNotFoundError):
            # Некорректный файл блокировки - удалить
            self.lock_file.unlink(missing_ok=True)
            return False
    
    def acquire(self) -> bool:
        """
        Захватывает блокировку для текущего экземпляра.
        
        Returns:
            True если блокировка успешно захвачена, False если приложение уже запущено
        """
        if self.is_already_running():
            return False
        
        # Создать файл блокировки с текущим PID
        try:
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except Exception:
            return False
    
    def release(self):
        """Освобождает блокировку при завершении приложения."""
        if self.lock_file and self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except Exception:
                pass
    
    def __enter__(self):
        """Контекстный менеджер - вход."""
        if not self.acquire():
            raise RuntimeError(f"{self.app_name} уже запущен!")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход."""
        self.release()
