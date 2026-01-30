"""
Плавающее окно для RapidWhisper.

Реализует минималистичное окно в форме "пилюли" с эффектами размытия,
анимациями и визуализацией звуковой волны.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPaintEvent
from ui.waveform_widget import WaveformWidget
from ui.info_panel_widget import InfoPanelWidget
from services.window_monitor import WindowMonitor
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
        
        # Для перетаскивания окна
        self._drag_position = None
        self._is_dragging = False
        
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
        
        # Window monitor и info panel (инициализируются позже через set_config)
        self.window_monitor: Optional[WindowMonitor] = None
        self.info_panel: Optional[InfoPanelWidget] = None
    
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
        
        # Сохраняем layout для последующего добавления info_panel
        self._main_layout = layout
        
        self.setLayout(layout)
    
    def set_config(self, config) -> None:
        """
        Устанавливает конфигурацию и инициализирует window monitor и info panel.
        
        Args:
            config: Объект конфигурации приложения
        
        Requirements: 7.1
        """
        try:
            # Создать window monitor
            self.window_monitor = WindowMonitor.create()
            
            # Создать info panel
            self.info_panel = InfoPanelWidget(config, self)
            
            # Добавить info panel в конец layout
            self._main_layout.addWidget(self.info_panel)
            
            # Обновить высоту окна с учетом info panel
            self.window_height = 120 + 40  # Исходная высота + высота info panel
            self.setFixedSize(self.window_width, self.window_height)
            
        except Exception as e:
            # Логировать ошибку, но не прерывать работу
            from utils.logger import get_logger
            logger = get_logger()
            logger.error(f"Failed to initialize window monitor and info panel: {e}")
    
    def show_at_center(self, use_saved_position: bool = True) -> None:
        """
        Показывает окно в центре экрана или в сохраненной позиции с fade-in анимацией.
        
        Вычисляет центр экрана и позиционирует окно, затем
        анимирует появление.
        
        Args:
            use_saved_position: Использовать сохраненную позицию если доступна
        
        Requirements: 2.2, 2.7
        """
        from PyQt6.QtWidgets import QApplication
        from dotenv import load_dotenv
        from core.config import get_env_path
        import os
        
        # ВАЖНО: Перезагрузить переменные окружения перед чтением
        env_path = str(get_env_path())
        load_dotenv(env_path, override=True)
        
        # Получаем геометрию экрана
        app = QApplication.instance()
        screen = None
        geometry = None
        
        if app:
            screen = app.primaryScreen()
            if screen:
                geometry = screen.availableGeometry()
        
        # Определить позицию окна
        x, y = None, None
        
        if use_saved_position:
            # Проверить предустановленную позицию
            preset = os.getenv('WINDOW_POSITION_PRESET', 'center')
            
            # Логирование для отладки
            from utils.logger import get_logger
            logger = get_logger()
            logger.info(f"Показ окна: preset={preset}, remember={os.getenv('REMEMBER_WINDOW_POSITION', 'true')}")
            
            if preset == 'custom':
                # Использовать пользовательскую позицию
                saved_pos = self.load_position()
                if saved_pos:
                    x, y = saved_pos
            elif geometry:
                # Использовать предустановленную позицию
                margin = 20  # Отступ от краев экрана
                
                if preset == 'center':
                    x = geometry.center().x() - self.window_width // 2
                    y = geometry.center().y() - self.window_height // 2
                elif preset == 'top_left':
                    x = geometry.left() + margin
                    y = geometry.top() + margin
                elif preset == 'top_right':
                    x = geometry.right() - self.window_width - margin
                    y = geometry.top() + margin
                elif preset == 'bottom_left':
                    x = geometry.left() + margin
                    y = geometry.bottom() - self.window_height - margin
                elif preset == 'bottom_right':
                    x = geometry.right() - self.window_width - margin
                    y = geometry.bottom() - self.window_height - margin
        
        # Если позиция не определена, использовать центр
        if x is None or y is None:
            if geometry:
                x = geometry.center().x() - self.window_width // 2
                y = geometry.center().y() - self.window_height // 2
            else:
                x, y = 100, 100  # Fallback позиция
        
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
        
        # Запустить мониторинг активного окна
        self._start_window_monitoring()
    
    def hide_with_animation(self) -> None:
        """
        Скрывает окно с fade-out анимацией.
        
        Анимирует исчезновение окна и скрывает его после завершения.
        
        Requirements: 2.8
        """
        self._stop_window_monitoring()
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
    
    def mousePressEvent(self, event) -> None:
        """
        Обрабатывает нажатие кнопки мыши для начала перетаскивания.
        
        Args:
            event: Событие нажатия мыши
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            # Изменить курсор на "перемещение"
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event) -> None:
        """
        Обрабатывает перемещение мыши для перетаскивания окна.
        
        Args:
            event: Событие перемещения мыши
        """
        if self._is_dragging and self._drag_position is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_position
            self.move(new_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event) -> None:
        """
        Обрабатывает отпускание кнопки мыши для завершения перетаскивания.
        
        Args:
            event: Событие отпускания мыши
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._drag_position = None
            event.accept()
            # Вернуть обычный курсор
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # Сохранить позицию окна
            self.save_position()
    
    def enterEvent(self, event) -> None:
        """
        Обрабатывает наведение курсора на окно.
        
        Отменяет автоскрытие при наведении курсора и меняет курсор.
        
        Args:
            event: Событие наведения
        
        Requirements: 8.7
        """
        self.cancel_auto_hide_timer()
        # Показать, что окно можно перетаскивать
        if not self._is_dragging:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """
        Обрабатывает уход курсора с окна.
        
        Возобновляет таймер автоскрытия при уходе курсора.
        
        Args:
            event: Событие ухода
        
        Requirements: 8.7
        """
        # Вернуть обычный курсор
        if not self._is_dragging:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)
    
    def closeEvent(self, event) -> None:
        """
        Обрабатывает закрытие окна.
        
        Останавливает мониторинг активного окна при закрытии.
        
        Args:
            event: Событие закрытия
        
        Requirements: 7.4
        """
        self._stop_window_monitoring()
        super().closeEvent(event)
    
    def _start_window_monitoring(self) -> None:
        """
        Запускает мониторинг активного окна.
        
        Подключает callback для обновления info panel при изменении
        активного окна.
        
        Requirements: 7.3
        """
        try:
            if self.window_monitor and self.info_panel:
                self.window_monitor.start_monitoring(self.info_panel.update_app_info)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger()
            logger.error(f"Failed to start window monitoring: {e}")
    
    def _stop_window_monitoring(self) -> None:
        """
        Останавливает мониторинг активного окна.
        
        Requirements: 7.4
        """
        try:
            if self.window_monitor:
                self.window_monitor.stop_monitoring()
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger()
            logger.error(f"Failed to stop window monitoring: {e}")
    
    def save_position(self) -> None:
        """
        Сохраняет текущую позицию окна в конфигурацию.
        Сохраняет только если настройка REMEMBER_WINDOW_POSITION включена.
        При перетаскивании автоматически устанавливает preset в "custom".
        """
        try:
            from core.config import get_env_path
            import os
            
            env_path = str(get_env_path())
            
            # Проверить, включена ли настройка запоминания позиции
            remember = os.getenv('REMEMBER_WINDOW_POSITION', 'true').lower()
            if remember not in ('true', '1', 'yes'):
                # Настройка выключена - не сохранять позицию
                return
            
            # Получить текущую позицию
            pos = self.pos()
            x, y = pos.x(), pos.y()
            
            # Прочитать существующий .env
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_lines = f.readlines()
            
            # Обновить или добавить позицию
            position_x_found = False
            position_y_found = False
            preset_found = False
            
            for i, line in enumerate(env_lines):
                if line.strip().startswith('WINDOW_POSITION_X='):
                    env_lines[i] = f'WINDOW_POSITION_X={x}\n'
                    position_x_found = True
                elif line.strip().startswith('WINDOW_POSITION_Y='):
                    env_lines[i] = f'WINDOW_POSITION_Y={y}\n'
                    position_y_found = True
                elif line.strip().startswith('WINDOW_POSITION_PRESET='):
                    env_lines[i] = f'WINDOW_POSITION_PRESET=custom\n'
                    preset_found = True
            
            # Добавить если не найдено
            if not position_x_found:
                env_lines.append(f'WINDOW_POSITION_X={x}\n')
            if not position_y_found:
                env_lines.append(f'WINDOW_POSITION_Y={y}\n')
            if not preset_found:
                env_lines.append(f'WINDOW_POSITION_PRESET=custom\n')
            
            # Сохранить обратно
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_lines)
                
        except Exception as e:
            # Игнорируем ошибки сохранения позиции
            pass
    
    def load_position(self) -> tuple[int, int] | None:
        """
        Загружает сохраненную позицию окна из конфигурации.
        
        Returns:
            Кортеж (x, y) с позицией или None если позиция не сохранена
        """
        try:
            import os
            
            x = os.getenv('WINDOW_POSITION_X')
            y = os.getenv('WINDOW_POSITION_Y')
            
            if x is not None and y is not None:
                return (int(x), int(y))
        except:
            pass
        
        return None
