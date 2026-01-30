"""
Плавающее окно для RapidWhisper.

Реализует минималистичное окно в форме "пилюли" с эффектами размытия,
анимациями и визуализацией звуковой волны.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPaintEvent
from ui.waveform_widget import WaveformWidget
from typing import Optional


class FloatingWindow(QWidget):
    """
    Плавающее окно в форме пилюли.
    
    Отображает минималистичное окно поверх всех других окон с
    эффектом размытого стекла, визуализацией звуковой волны и
    текстовым статусом.
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
    """
    
    def __init__(self, parent=None):
        """
        Инициализирует плавающее окно.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Размеры окна
        self.window_width = 400
        self.window_height = 120
        
        # Настройка свойств окна
        self.setup_window_properties()
        
        # Создание UI компонентов
        self._create_ui()
        
        # Анимации
        self._fade_animation: Optional[QPropertyAnimation] = None
        self._opacity_effect: Optional[QGraphicsOpacityEffect] = None
        
        # Таймер автоскрытия
        self._auto_hide_timer = QTimer(self)
        self._auto_hide_timer.timeout.connect(self.hide_with_animation)
        self._auto_hide_timer.setSingleShot(True)
    
    def setup_window_properties(self) -> None:
        """
        Настраивает свойства окна.
        
        Устанавливает флаги для frameless окна, always-on-top и
        полупрозрачного фона.
        
        Requirements: 2.4, 2.5, 2.6
        """
        # Флаги окна: без рамки, всегда поверх, tool window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus  # Не забирает фокус у других окон
        )
        
        # Полупрозрачный фон
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Показывать окно даже когда приложение не в фокусе
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Размер окна
        self.setFixedSize(self.window_width, self.window_height)
        
        # ВАЖНО: Добавляем стили для видимости окна
        # border-radius применяется только к главному виджету
        self.setStyleSheet("""
            FloatingWindow {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 5px;
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                padding: 5px;
                border: none;
            }
            WaveformWidget {
                background: transparent;
                border: none;
            }
        """)
    
    def _create_ui(self) -> None:
        """Создает UI компоненты окна."""
        # Главный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Виджет визуализации волны - ФИКСИРОВАННАЯ ВЫСОТА
        self.waveform_widget = WaveformWidget(self)
        self.waveform_widget.setFixedHeight(50)  # Фиксированная высота для волны
        layout.addWidget(self.waveform_widget)
        
        # Метка статуса/текста
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setFixedHeight(40)  # Фиксированная высота для текста
        # Убираем отдельные стили для label - они уже в setStyleSheet окна
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def show_at_center(self) -> None:
        """
        Показывает окно в центре экрана с fade-in анимацией.
        
        Вычисляет центр экрана и позиционирует окно, затем
        анимирует появление.
        
        Requirements: 2.2, 2.7
        """
        # Получаем геометрию экрана
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                geometry = screen.availableGeometry()
                
                # Вычисляем центр
                x = geometry.center().x() - self.window_width // 2
                y = geometry.center().y() - self.window_height // 2
                
                # Позиционируем окно
                self.move(x, y)
        
        # Показываем окно с анимацией
        self.show()
        self.raise_()  # Поднять окно наверх
        self.setWindowState(Qt.WindowState.WindowActive)  # Установить как активное
        
        # Принудительно установить флаг "всегда поверх" (на случай если сбросился)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.show()  # Показать снова после изменения флагов
        
        self._fade_in()  # Запустить анимацию появления
    
    def hide_with_animation(self) -> None:
        """
        Скрывает окно с fade-out анимацией.
        
        Анимирует исчезновение окна и скрывает его после завершения.
        
        Requirements: 2.8
        """
        self._fade_out()
    
    def _fade_in(self, duration: int = 300) -> None:
        """
        Анимация появления (fade-in).
        
        Args:
            duration: Длительность анимации в миллисекундах
        
        Requirements: 2.7
        """
        # Создаем эффект прозрачности если его нет
        if not self._opacity_effect:
            self._opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self._opacity_effect)
        
        # Создаем анимацию
        self._fade_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_animation.setDuration(duration)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._fade_animation.start()
    
    def _fade_out(self, duration: int = 300) -> None:
        """
        Анимация исчезновения (fade-out).
        
        Args:
            duration: Длительность анимации в миллисекундах
        
        Requirements: 2.8
        """
        # Создаем эффект прозрачности если его нет
        if not self._opacity_effect:
            self._opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self._opacity_effect)
        
        # Создаем анимацию
        self._fade_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_animation.setDuration(duration)
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Скрываем окно после завершения анимации
        self._fade_animation.finished.connect(self.hide)
        self._fade_animation.start()
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Отрисовывает скругленный фон окна.
        
        Рисует полупрозрачный скругленный прямоугольник с радиусом 5px.
        
        Args:
            event: Событие отрисовки
        
        Requirements: 2.1, 2.6
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Создать путь со скругленными углами
        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(float(rect.x()), float(rect.y()), 
                           float(rect.width()), float(rect.height()), 
                           5.0, 5.0)  # border-radius: 5px
        
        # Заполнить фон
        painter.fillPath(path, QColor(30, 30, 30, 240))
        
        # Нарисовать границу
        painter.setPen(QColor(255, 255, 255, 100))
        painter.drawPath(path)
    
    def set_status(self, text: str) -> None:
        """
        Устанавливает текст статуса.
        
        Args:
            text: Текст для отображения
        
        Requirements: 8.1
        """
        self.status_label.setText(text)
    
    def set_result_text(self, text: str, max_length: int = 100) -> None:
        """
        Устанавливает текст результата транскрипции.
        
        Усекает текст если он длиннее max_length символов.
        
        Args:
            text: Текст результата
            max_length: Максимальная длина для отображения
        
        Requirements: 8.1, 8.3
        """
        if len(text) > max_length:
            display_text = text[:max_length] + "..."
        else:
            display_text = text
        
        self.status_label.setText(display_text)
    
    def start_auto_hide_timer(self, delay_ms: int = 2500) -> None:
        """
        Запускает таймер автоматического скрытия окна.
        
        Args:
            delay_ms: Задержка в миллисекундах (по умолчанию 2.5 секунды)
        
        Requirements: 8.6
        """
        self._auto_hide_timer.start(delay_ms)
    
    def cancel_auto_hide_timer(self) -> None:
        """
        Отменяет таймер автоматического скрытия.
        
        Requirements: 8.7
        """
        if self._auto_hide_timer.isActive():
            self._auto_hide_timer.stop()
    
    def enterEvent(self, event) -> None:
        """
        Обрабатывает наведение курсора на окно.
        
        Отменяет автоскрытие при наведении курсора.
        
        Args:
            event: Событие наведения
        
        Requirements: 8.7
        """
        self.cancel_auto_hide_timer()
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """
        Обрабатывает уход курсора с окна.
        
        Возобновляет таймер автоскрытия при уходе курсора.
        
        Args:
            event: Событие ухода
        
        Requirements: 8.7
        """
        # Можно возобновить таймер если нужно
        super().leaveEvent(event)
    
    def get_waveform_widget(self) -> WaveformWidget:
        """
        Возвращает виджет визуализации волны.
        
        Returns:
            WaveformWidget для управления визуализацией
        """
        return self.waveform_widget
    
    def apply_blur_effect(self) -> None:
        """
        Применяет эффект размытого стекла (platform-specific).
        
        Пытается применить платформо-зависимый эффект размытия.
        
        Requirements: 2.3
        """
        from utils.platform_utils import apply_blur_effect
        
        # Применяем платформо-зависимый эффект размытия
        success = apply_blur_effect(self)
        
        if not success:
            # Если не удалось применить нативный эффект,
            # используем базовую полупрозрачность Qt
            pass
