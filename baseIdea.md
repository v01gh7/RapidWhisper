# ТЗ: Клон SuperWhisper на GLM (Python)

## 1. Концепция и Визуальный стиль (100% как SuperWhisper)
Приложение должно выглядеть не как обычная программа, а как современный macOS/Windows виджет.

### 1.1. Интерфейс (UI)
*   **Форма:** "Пилюля" (Pill) или скругленный прямоугольник. Появляется поверх всех окон.
*   **Позиционирование:** По центру экрана или рядом с курсором мыши при активации.
*   **Эффекты:**
    *   Размытый фон (Frosted Glass / Acrylic effect).
    *   Минималистичный дизайн без лишних кнопок.
*   **Анимация записи:** Динамическая звуковая волна (Waveform) в центре "пилюли", которая пульсирует в такт голосу. **Это критично для ощущения работы программы.**

### 1.2. Сценарий работы (UX Flow)
1.  **Hotkey:** Нажимается глобальная клавиша (например, `F1`).
2.  **Появление:** На экране появляется "плавающая кнопка" с анимацией волны.
3.  **Запись:** Пользователь говорит (волна дышит).
4.  **Тишина / Повторное нажатие:** Запись заканчивается.
5.  **Обработка:** Волна превращается в спиннер загрузки.
6.  **Результат:**
    *   Текст мгновенно появляется внутри этой же "плавающей кнопки".
    *   **Действие:** Текст **автоматически копируется в буфер обмена**.
    *   **Финал:** Окно плавно исчезает через 2-3 секунды или остается до следующего Hotkey.

---

## 2. Технологический Стек

1.  **Язык:** Python 3.11+
2.  **GUI Framework:** **PyQt6** (PySide6). Это единственная библиотека, которая позволяет делать кастомные окна с размытием (blur) без боли.
3.  **Аудио:** **PyAudio** (или sounddevice) + **NumPy** (для визуализации волны).
4.  **AI SDK:** **OpenAI Python Library** (`pip install openai`).
    *   *Обоснование:* Ты попросил использовать "OpenAI SDK", так как GLM поддерживает совместимость. Мы будем использовать клиент OpenAI, но переключать `base_url` на сервер Zhipu AI.
5.  **Буфер обмена:** **Pyperclip**.

---

## 3. Архитектура и Реализация

### 3.1. Настройка AI (Zhipu GLM via OpenAI SDK)
Мы используем класс `openai.OpenAI`, но конфигурируем его на API Zhipu.

```python
from openai import OpenAI

# Инициализация клиента GLM через SDK OpenAI
client = OpenAI(
    api_key="ТВОЙ_GLM_API_KEY",
    base_url="https://open.bigmodel.cn/api/paas/v4/audio/transcriptions" # Проверь актуальный эндпоинт для транскрибации GLM
)

def transcribe_audio(file_path):
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", # GLM обычно мапит свой аудио движок сюда
            file=open(file_path, "rb"),
            language="ru" # Язык транскрибации
        )
        return transcript.text
    except Exception as e:
        print(f"GLM API Error: {e}")
        return None
```

### 3.2. Визуализация Звуковой Волны (Ключевой момент)
Не просто статус "Запись", а реальные бары, которые прыгают от громкости.

*   Логика: В `PyQt6` используем `QTimer` с интервалом ~50мс.
*   В каждом такте считываем текущий уровень громкости (RMS) из аудиопотока.
*   Отрисовываем в `paintEvent` круг/линию, высота которой зависит от громкости.

```python
# Пример логики для визуализации (в упрощенном виде)
def update_audio_level(self):
    if self.is_recording:
        data = self.stream.read(self.chunk_size)
        volume = np.sqrt(np.mean(data**2)) # RMS
        # Передаем уровень громкости в UI для отрисовки анимации
        self.floating_window.set_wave_height(volume * 50)
```

### 3.3. Управление Окном (Floating Window)
Окно должно быть **Tool Window** (флаг `Qt.WindowType.Tool` или `WindowStaysOnTopHint`) и **Frameless** (`Qt.FramelessWindowHint`).

*   **Цвет фона:** Полупрозрачный, например, `rgba(0, 0, 0, 150)`.
*   **Скругление:** CSS стили для PyQt: `border-radius: 30px;`.

---

## 4. Техническое Задание для Разработчика (Список задач)

### Задача 1: Фреймворк и Окно
1.  Создать приложение на PyQt6.
2.  Настроить "плавающее окно" без рамки, всегда поверх всех окон.
3.  Реализовать эффект размытия (BackdropFilter) для Windows 11 / macOS.
4.  Настроить глобальную горячую клавишу (например, через библиотеку `keyboard`).

### Задача 2: Аудио Движок
1.  Инициализировать поток записи с микрофона.
2.  Реализовать детектор тишины (Silence Detection):
    *   Если RMS < Threshold 1.5 сек -> `stop_recording()`.
3.  Выводить данные громкости в отдельный сигнал для UI.

### Задача 3: UI Анимация
1.  Создать виджет внутри окна для отрисовки волн (Canvas или QPainter).
2.  Сделать анимацию "вдоха" (Waveform) во время записи.
3.  Сделать анимацию "пульсации" (Indeterminate Progress Bar) во время отправки в GLM.
4.  Сделать анимацию появления текста (Fade In).

### Задача 4: Интеграция GLM API
1.  Сохранить аудио во временный `.wav` файл (или mp3, если SDK требует).
2.  Отправить запрос в Zhipu AI через `openai` SDK (как показано в пункте 3.1).
3.  Получить JSON-ответ, извлечь `text`.

### Задача 5: Финализация
1.  Отобразить полученный текст в окне (показать первые 50-100 символов, остальное обрезать или сделать скролл).
2.  Скопировать **весь** текст в буфер обмена (`pyperclip.copy()`).
3.  Показать уведомление "Текст скопирован".
4.  Через 2 секунды свернуть окно (или скрыть виджет) в ожидание следующего нажатия.

---

## 5. Требование к скорости (Performance)
*   **Задержка записи -> отправка:** Мгновенно.
*   **Скорость ответа GLM:** GLM работает быстро. Вся цепочка (конец речи -> текст в буфере) должна занимать **1-2 секунды** (с учетом интернет-соединения).
*   **UI:** Никаких лагов анимации волны. Запись и отрисовка должны быть в разных потоках.

---

## 6. Пример кода (Skeleton)

```python
import sys
import numpy as np
import pyaudio
import keyboard
import pyperclip
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from openai import OpenAI

class SuperGLMWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        self.init_audio()
        
        # Настройка GLM клиента
        self.glm_client = OpenAI(
            api_key="YOUR_KEY",
            base_url="https://open.bigmodel.cn/api/paas/v4/audio/transcriptions" 
        )

    def init_ui(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Нажми Alt+S", self)
        self.status_label.setStyleSheet("color: white; font-size: 18px;")
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def start_recording(self):
        self.show()
        # Запуск потока записи
        # Запуск таймера для анимации волны
        pass

    def stop_recording(self, file_path):
        # Остановка записи
        # Отправка в GLM
        text = self.send_to_glm(file_path)
        self.show_result(text)

    def send_to_glm(self, path):
        try:
            with open(path, "rb") as audio_file:
                transcript = self.glm_client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                return transcript.text
        except Exception as e:
            print(e)
            return "Ошибка"

    def show_result(self, text):
        pyperclip.copy(text)
        self.status_label.setText(text)
        # Таймер на закрытие окна через 2 сек
        QTimer.singleShot(2000, self.hide)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SuperGLMWidget()
    
    # Хук хоткея
    keyboard.add_hotkey('alt+s', widget.start_recording)
    
    sys.exit(app.exec())
```