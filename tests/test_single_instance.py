"""
Тесты для модуля single_instance.

Проверяет работу механизма единственного экземпляра приложения.
"""

import pytest
import os
import tempfile
from pathlib import Path
from utils.single_instance import SingleInstance


def test_single_instance_first_run():
    """Тест: Первый запуск приложения должен успешно захватить блокировку."""
    instance = SingleInstance("TestApp")
    
    # Первый запуск - должен успешно захватить блокировку
    assert instance.acquire() is True
    assert instance.is_already_running() is True
    
    # Освободить блокировку
    instance.release()
    assert instance.is_already_running() is False


def test_single_instance_second_run():
    """Тест: Второй запуск приложения должен обнаружить что приложение уже запущено."""
    instance1 = SingleInstance("TestApp2")
    instance2 = SingleInstance("TestApp2")
    
    # Первый экземпляр захватывает блокировку
    assert instance1.acquire() is True
    
    # Второй экземпляр должен обнаружить что приложение уже запущено
    assert instance2.is_already_running() is True
    assert instance2.acquire() is False
    
    # Освободить блокировку
    instance1.release()
    
    # Теперь второй экземпляр может захватить блокировку
    assert instance2.acquire() is True
    instance2.release()


def test_single_instance_context_manager():
    """Тест: Использование SingleInstance как контекстного менеджера."""
    # Первый экземпляр
    with SingleInstance("TestApp3") as instance:
        assert instance.is_already_running() is True
        
        # Попытка создать второй экземпляр должна вызвать исключение
        with pytest.raises(RuntimeError, match="уже запущен"):
            with SingleInstance("TestApp3"):
                pass
    
    # После выхода из контекста блокировка должна быть освобождена
    instance2 = SingleInstance("TestApp3")
    assert instance2.is_already_running() is False


def test_single_instance_stale_lock():
    """Тест: Обработка устаревшего файла блокировки."""
    instance = SingleInstance("TestApp4")
    
    # Создать фейковый файл блокировки с несуществующим PID
    with open(instance.lock_file, 'w') as f:
        f.write("999999")  # Несуществующий PID
    
    # Должен обнаружить что процесс не существует и удалить файл
    assert instance.is_already_running() is False
    
    # Должен успешно захватить блокировку
    assert instance.acquire() is True
    instance.release()


def test_single_instance_cleanup():
    """Тест: Очистка файла блокировки при освобождении."""
    instance = SingleInstance("TestApp5")
    
    # Захватить блокировку
    assert instance.acquire() is True
    assert instance.lock_file.exists()
    
    # Освободить блокировку
    instance.release()
    assert not instance.lock_file.exists()
