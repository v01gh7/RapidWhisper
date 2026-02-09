"""
Плавающее окно для RapidWhisper.

Реализует минималистичное окно в форме "пилюли" с эффектами размытия,
анимациями и визуализацией звуковой волны.
"""

import time

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPaintEvent
from ui.waveform_widget import WaveformWidget
from ui.info_panel_widget import InfoPanelWidget
from design_system.styled_window_mixin import StyledWindowMixin
from design_system.window_themes import DEFAULT_WINDOW_THEME_ID, get_window_theme
from services.window_monitor import WindowMonitor
from utils.i18n import t
from typing import Optional

INTERBAL_WINDOW_BORDER_RADIUS = 18.0

class FloatingWindow(QWidget, StyledWindowMixin):
    """
    Плавающее окно в форме пилюли.
    
    Отображает минималистичное окно поверх всех других окон с
    эффектом размытого стекла, визуализацией звуковой волны и
    текстовым статусом.
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
    """
    
    def __init__(self, config=None, parent=None):
        """
        Инициализирует плавающее окно.
        
        Args:
            config: Объект конфигурации приложения (опциональный)
            parent: Родительский виджет
        """
        QWidget.__init__(self, parent)
        StyledWindowMixin.__init__(self)
        # Floating window now uses opaque themed rendering only.
        self._native_blur_enabled = False
        
        # Сохранить конфигурацию
        self.config = config
        self._theme_id = getattr(config, "window_theme", DEFAULT_WINDOW_THEME_ID)
        self._theme = get_window_theme(self._theme_id)
        
        # Keep background fully opaque.
        self._opacity = 255
        if self.config is not None:
            self.config.window_opacity = 255
        
        # Размеры окна (будут пересчитаны динамически)
        self.window_width = 600
        self._base_height = 110
        self._recording_height = 152
        self.window_height = self._base_height
        self._min_width = 600  # Минимальная ширина (увеличена для лучшего spacing)
        self._max_width_percent = 0.3  # Максимум 30% ширины экрана
        
        # Для перетаскивания окна
        self._drag_position = None
        self._is_dragging = False
        self._corner_radius = int(INTERBAL_WINDOW_BORDER_RADIUS)
        
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

        # Таймер записи для отображения времени
        self._recording_timer = QTimer(self)
        self._recording_timer.setInterval(1000)
        self._recording_timer.timeout.connect(self._update_recording_timer)
        self._recording_start_time: Optional[float] = None
        
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
            Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus  # Не забирает фокус у других окон
        )
        
        # Полупрозрачная поверхность и реальная форма окна управляются единообразно.
        self.configure_translucent_surface(self._corner_radius)
        
        # Показывать окно даже когда приложение не в фокусе
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Размер окна - будет пересчитан динамически
        self.setMinimumWidth(self._min_width)
        self.setFixedHeight(self.window_height)
        
        # Применить прозрачность из конфигурации
        self._apply_opacity()
    
    def _create_ui(self) -> None:
        """Создает UI компоненты окна."""
        # Главный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(6)

        # Верхняя строка записи (точка + статус слева, таймер справа)
        self.recording_header = QWidget(self)
        self.recording_header.setObjectName("recordingHeader")
        self.recording_header.setFixedHeight(20)
        header_layout = QHBoxLayout(self.recording_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self._record_dot = QLabel("", self.recording_header)
        self._record_dot.setObjectName("recordDot")
        self._record_dot.setFixedSize(8, 8)

        self._recording_status_label = QLabel("", self.recording_header)
        self._recording_status_label.setObjectName("recordStatus")
        self._recording_status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._recording_time_label = QLabel("00:00", self.recording_header)
        self._recording_time_label.setObjectName("recordTime")
        self._recording_time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(self._record_dot)
        header_layout.addWidget(self._recording_status_label)
        header_layout.addStretch()
        header_layout.addWidget(self._recording_time_label)

        self.recording_header.hide()
        layout.addWidget(self.recording_header)
        
        # Виджет визуализации волны - ФИКСИРОВАННАЯ ВЫСОТА
        self.waveform_widget = WaveformWidget(self, self.config)
        self.waveform_widget.setFixedHeight(56)  # Фиксированная высота для волны
        layout.addWidget(self.waveform_widget)
        
        # Метка статуса/текста
        self.status_label = QLabel("", self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setFixedHeight(28)  # Фиксированная высота для текста
        # Убираем отдельные стили для label - они уже в setStyleSheet окна
        layout.addWidget(self.status_label)
        
        # Сохраняем layout для последующего добавления info_panel
        self._main_layout = layout
        
        self.setLayout(layout)
    
    def _apply_opacity(self) -> None:
        """
        Применяет текущую прозрачность к окну.
        
        Обновляет stylesheet с текущим значением прозрачности.
        
        Requirements: 1.2, 1.3
        """
        self._opacity = 255

        # Получить размер шрифта из конфигурации
        font_size = self.config.font_size_floating_main if self.config else 14
        info_font_size = max(10, font_size - 3)
        
        # Фон top-level окна рисуется только в paintEvent.
        self.setStyleSheet(f"""
            FloatingWindow {{
                background: transparent;
                border: none;
            }}
            QLabel {{
                color: {self._theme["text_primary"]};
                font-size: {font_size}px;
                font-family: '{self._theme["font_family"]}';
                background: transparent;
                padding: 0;
                border: none;
            }}
            QLabel#statusLabel {{
                padding: 2px 2px;
            }}
            QLabel#recordStatus {{
                font-size: {info_font_size}px;
                font-weight: 500;
                color: {self._theme["text_secondary"]};
            }}
            QLabel#recordTime {{
                font-size: {info_font_size}px;
                font-weight: 600;
                color: {self._theme["text_secondary"]};
            }}
            QLabel#recordDot {{
                background-color: {self._theme["record_dot"]};
                border-radius: 4px;
            }}
            WaveformWidget {{
                background: transparent;
                border: none;
            }}
        """)
        self._set_waveform_color()
        self.update()  # Trigger repaint
    
    def set_opacity(self, value: int) -> None:
        """
        Устанавливает прозрачность окна (вызывается из настроек).
        
        Args:
            value: Значение прозрачности (50-255)
        
        Requirements: 1.2
        """
        # Opacity is fixed to fully opaque mode.
        self._opacity = 255
        if self.config is not None:
            self.config.window_opacity = 255
        self._apply_opacity()

    def set_theme(self, theme_id: str, update_waveform: bool = True) -> None:
        """Applies a predefined floating-window theme."""
        self._theme_id = theme_id or DEFAULT_WINDOW_THEME_ID
        self._theme = get_window_theme(self._theme_id)
        if self.config is not None:
            self.config.window_theme = self._theme_id
            self.config.window_opacity = 255
            if update_waveform:
                self.config.waveform_color = self._theme["waveform_color"]
                self._set_waveform_color()
        self._apply_opacity()
        if self.info_panel and hasattr(self.info_panel, "set_theme"):
            self.info_panel.set_theme(self._theme_id)

    def _set_waveform_color(self) -> None:
        """Syncs waveform color from config/theme to waveform widget."""
        if not hasattr(self, "waveform_widget") or self.waveform_widget is None:
            return
        if self.config and getattr(self.config, "waveform_color", ""):
            color = self.config.waveform_color
        else:
            color = self._theme["waveform_color"]
        self.waveform_widget.set_waveform_color(color)
    
    def set_config(self, config) -> None:
        """
        Устанавливает конфигурацию и инициализирует window monitor и info panel.
        
        Args:
            config: Объект конфигурации приложения
        
        Requirements: 7.1
        """
        self.config = config
        if self.config is not None:
            self.config.window_opacity = 255
        self._theme_id = getattr(config, "window_theme", DEFAULT_WINDOW_THEME_ID)
        self._theme = get_window_theme(self._theme_id)

        try:
            # Создать window monitor
            self.window_monitor = WindowMonitor.create()
            
            # Создать info panel
            self.info_panel = InfoPanelWidget(config, self)
            if hasattr(self.info_panel, "set_theme"):
                self.info_panel.set_theme(self._theme_id)
            
            # Добавить info panel в конец layout
            self._main_layout.addWidget(self.info_panel)
            
            # СКРЫТЬ info panel по умолчанию (показывается только при записи)
            self.info_panel.hide()
            
            # Высота окна в неактивном режиме (info panel скрыта)
            self._set_fixed_height(self._base_height)
            
            # Пересчитать ширину окна
            self._update_window_width()
            self._sync_info_panel_width()
            self._set_waveform_color()
            self._apply_opacity()
            
        except Exception as e:
            # Логировать ошибку, но не прерывать работу
            from utils.logger import get_logger
            logger = get_logger()
            logger.error(f"Failed to initialize window monitor and info panel: {e}")
    
    def get_info_panel(self) -> Optional[InfoPanelWidget]:
        """
        Возвращает виджет информационной панели.
        
        Returns:
            InfoPanelWidget или None если не инициализирован
        """
        return self.info_panel
    
    def show_info_panel(self) -> None:
        """Показывает info panel."""
        if self.info_panel and not self.info_panel.isVisible():
            self.info_panel.show()
        self._set_fixed_height(self._recording_height)
        self._stabilize_geometry()
    
    def hide_info_panel(self) -> None:
        """Скрывает info panel."""
        if self.info_panel and self.info_panel.isVisible():
            self.info_panel.hide()
        self._set_fixed_height(self._base_height)
        self._stabilize_geometry()
    
    def _update_window_width(self) -> None:
        """
        Обновляет ширину окна на основе контента.
        
        Автоматически подстраивает ширину под контент info panel,
        но не превышает 30% ширины экрана.
        """
        if not self.info_panel:
            return
        
        from PyQt6.QtWidgets import QApplication
        
        # Получить размер контента info panel
        self.info_panel.adjustSize()
        content_width = self.info_panel.sizeHint().width()
        
        # Добавить отступы окна (margins + padding)
        total_width = content_width + 36  # 18px слева + 18px справа
        
        # Получить максимальную ширину (30% экрана)
        app = QApplication.instance()
        max_width = self._min_width
        if app:
            screen = app.primaryScreen()
            if screen:
                screen_width = screen.availableGeometry().width()
                max_width = int(screen_width * self._max_width_percent)
        
        # Ограничить ширину
        final_width = max(self._min_width, min(total_width, max_width))
        
        # Установить новую ширину
        self.window_width = final_width
        self.setFixedWidth(final_width)
        self._sync_info_panel_width()
    
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
        from core.config_loader import get_config_loader
        
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
            # Проверить предустановленную позицию из config.jsonc
            config_loader = get_config_loader()
            preset = config_loader.get('window.position_preset', 'center')
            
            # Логирование для отладки
            from utils.logger import get_logger
            logger = get_logger()
            remember = config_loader.get('window.remember_position', True)
            logger.info(f"Показ окна: preset={preset}, remember={remember}")
            
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
                elif preset == 'top_center':
                    x = geometry.center().x() - self.window_width // 2
                    y = geometry.top() + margin
                elif preset == 'top_right':
                    x = geometry.right() - self.window_width - margin
                    y = geometry.top() + margin
                elif preset == 'center_left':
                    x = geometry.left() + margin
                    y = geometry.center().y() - self.window_height // 2
                elif preset == 'center_right':
                    x = geometry.right() - self.window_width - margin
                    y = geometry.center().y() - self.window_height // 2
                elif preset == 'bottom_left':
                    x = geometry.left() + margin
                    y = geometry.bottom() - self.window_height - margin
                elif preset == 'bottom_center':
                    x = geometry.center().x() - self.window_width // 2
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
        # Не активируем окно, т.к. WindowDoesNotAcceptFocus

        # Держим контур и blur синхронизированными без пересоздания HWND.
        self.sync_rounded_surface(self._corner_radius)
        
        self._fade_in()  # Запустить анимацию появления
        
        # Запустить мониторинг активного окна
        self._start_window_monitoring()

    def resizeEvent(self, event) -> None:
        """Синхронизирует ширину инфопанели с доступной шириной окна."""
        super().resizeEvent(event)
        self._stabilize_geometry()
        self.sync_rounded_surface(self._corner_radius)

    def showEvent(self, event) -> None:
        """Обновляет маску окна при первом показе."""
        super().showEvent(event)
        self._stabilize_geometry()
        self.sync_rounded_surface(self._corner_radius)
    
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
        
        # ВАЖНО: Удалить эффект после завершения анимации
        # чтобы он не влиял на дочерние виджеты
        self._fade_animation.finished.connect(self._remove_opacity_effect)
        
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
    
    def _remove_opacity_effect(self) -> None:
        """
        Удаляет эффект прозрачности после завершения анимации.
        
        Это необходимо чтобы QGraphicsOpacityEffect не влиял на
        дочерние виджеты (InfoPanelWidget) после завершения анимации.
        """
        if self._opacity_effect:
            # Сначала убираем эффект с виджета
            self.setGraphicsEffect(None)
            # Затем очищаем ссылку
            self._opacity_effect = None
    
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
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        # Создать путь со скругленными углами (идентичный контуру mask/Win32 region).
        path = QPainterPath()
        rect_f = QRectF(self.rect())
        path.addRoundedRect(rect_f, float(self._corner_radius), float(self._corner_radius))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QColor(self._theme["floating_bg"]))

    def _update_window_mask(self) -> None:
        """Совместимость: обновление маски через общий mixin-метод."""
        self.apply_rounded_mask(self._corner_radius)
    
    def set_status(self, text: str) -> None:
        """
        Устанавливает текст статуса.
        
        Args:
            text: Текст для отображения
        
        Requirements: 8.1
        """
        # Всегда обновляем основной label (нужен для результатов/тестов)
        self.status_label.setText(text)

        if text == t("status.recording"):
            self._recording_status_label.setText(text)
            self._set_recording_header_visible(True)
            self._start_recording_timer()
        else:
            self._set_recording_header_visible(False)
            self._stop_recording_timer()
    
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
        
        self._set_recording_header_visible(False)
        self._stop_recording_timer()
        self.status_label.setText(display_text)
    
    def set_startup_message(self, text: str) -> None:
        """
        Устанавливает текст стартового сообщения с увеличенным шрифтом.
        
        Используется только для стартового окна при запуске программы.
        
        Args:
            text: Текст для отображения
        """
        # Скрыть waveform для стартового окна
        self._set_recording_header_visible(False)
        self._stop_recording_timer()
        self.waveform_widget.hide()
        
        # Убрать фиксированную высоту и дать label занять всё пространство
        self.status_label.setFixedHeight(0)  # Убрать фиксированную высоту
        self.status_label.setMinimumHeight(0)
        self.status_label.setMaximumHeight(16777215)  # Максимальное значение Qt
        
        # Применить специальный стиль для стартового сообщения
        # Центрирование по вертикали и горизонтали
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setText(text)
    
    def reset_status_style(self) -> None:
        """
        Сбрасывает стиль status_label к обычному.
        
        Вызывается после скрытия стартового окна.
        """
        # Показать waveform обратно
        self._set_recording_header_visible(False)
        self.waveform_widget.show()
        
        # Вернуть фиксированную высоту для label
        self.status_label.setFixedHeight(28)
        
        # Вернуть обычный стиль (из setStyleSheet окна)
        self.status_label.setStyleSheet("")
        # Вернуть обычное выравнивание (только по центру горизонтально)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
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
        # Централизованный путь: blur и форма окна поддерживаются в sync_rounded_surface.
        self.sync_rounded_surface(self._corner_radius)

    def _set_fixed_height(self, height: int) -> None:
        """Устанавливает фиксированную высоту и сохраняет значение."""
        self.window_height = height
        self.setFixedHeight(height)

    def _stabilize_geometry(self) -> None:
        """
        Keeps runtime geometry stable so first drag does not "fix" layout visually.
        """
        target_height = self._recording_height if (self.info_panel and self.info_panel.isVisible()) else self._base_height
        if self.window_height != target_height or self.height() != target_height:
            self._set_fixed_height(target_height)
        if hasattr(self, "waveform_widget") and self.waveform_widget is not None:
            if self.waveform_widget.height() != 56:
                self.waveform_widget.setFixedHeight(56)
        if hasattr(self, "_main_layout") and self._main_layout is not None:
            self._main_layout.activate()
        self._sync_info_panel_width()
        self.updateGeometry()

    def _sync_info_panel_width(self) -> None:
        """Принудительно растягивает info panel на доступную ширину."""
        if not self.info_panel or not self._main_layout:
            return
        margins = self._main_layout.contentsMargins()
        available_width = max(0, self.width() - margins.left() - margins.right())
        if self.info_panel.width() != available_width:
            self.info_panel.setFixedWidth(available_width)

    def _set_recording_header_visible(self, visible: bool) -> None:
        """Показывает/скрывает верхнюю строку записи и переключает основной статус."""
        if visible:
            self.recording_header.show()
            self.status_label.hide()
            self.status_label.setFixedHeight(0)
        else:
            self.recording_header.hide()
            self.status_label.show()
            self.status_label.setFixedHeight(28)
        self._stabilize_geometry()

    def _start_recording_timer(self) -> None:
        """Запускает таймер отображения времени записи."""
        self._recording_start_time = time.monotonic()
        self._recording_time_label.setText("00:00")
        if not self._recording_timer.isActive():
            self._recording_timer.start()

    def _stop_recording_timer(self) -> None:
        """Останавливает таймер записи."""
        if self._recording_timer.isActive():
            self._recording_timer.stop()
        self._recording_start_time = None

    def _update_recording_timer(self) -> None:
        """Обновляет отображение времени записи."""
        if self._recording_start_time is None:
            return
        elapsed = int(time.monotonic() - self._recording_start_time)
        minutes, seconds = divmod(elapsed, 60)
        self._recording_time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
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
            self._stabilize_geometry()
    
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
            from core.config_saver import get_config_saver
            from core.config_loader import get_config_loader
            import os
            
            # Проверить, включена ли настройка запоминания позиции
            config_loader = get_config_loader()
            remember = config_loader.get('window.remember_position', True)
            
            if not remember:
                # Настройка выключена - не сохранять позицию
                return
            
            # Получить текущую позицию
            pos = self.pos()
            x, y = pos.x(), pos.y()
            
            # Сохранить позицию и preset
            config_saver = get_config_saver()
            config_saver.update_multiple_values({
                'window.position_x': x,
                'window.position_y': y,
                'window.position_preset': 'custom'
            })
                
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
            from core.config_loader import get_config_loader
            
            config_loader = get_config_loader()
            x = config_loader.get('window.position_x')
            y = config_loader.get('window.position_y')
            
            if x is not None and y is not None:
                return (int(x), int(y))
        except:
            pass
        
        return None
