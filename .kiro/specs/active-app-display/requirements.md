# Requirements Document: Active App Display

## Introduction

Эта функция добавляет информационную панель в нижней части плавающего окна записи RapidWhisper, которая отображает текущее активное приложение и горячие клавиши. Панель помогает пользователю понимать контекст записи и напоминает о доступных горячих клавишах.

## Glossary

- **Active_Window**: Окно операционной системы, которое в данный момент находится в фокусе и получает ввод от пользователя
- **Floating_Window**: Плавающее окно RapidWhisper, которое отображается поверх всех окон во время записи
- **Info_Panel**: Нижняя панель в Floating_Window, отображающая информацию об активном приложении и горячих клавишах
- **App_Icon**: Иконка активного приложения, извлеченная из исполняемого файла или системных ресурсов
- **App_Name**: Название активного приложения или заголовок окна
- **Hotkey_Display**: Визуальное представление горячей клавиши в формате, понятном пользователю
- **Config_Manager**: Компонент системы конфигурации, управляющий настройками приложения
- **Window_Monitor**: Компонент, отслеживающий изменения активного окна в операционной системе

## Requirements

### Requirement 1: Отображение информации об активном приложении

**User Story:** Как пользователь, я хочу видеть, какое приложение было активно в момент начала записи, чтобы понимать контекст моей записи.

#### Acceptance Criteria

1. WHEN Floating_Window отображается, THEN Info_Panel SHALL показывать иконку и название текущего Active_Window
2. WHEN Active_Window изменяется во время отображения Floating_Window, THEN Info_Panel SHALL обновлять отображаемую информацию в течение 500ms
3. WHEN App_Icon недоступна для Active_Window, THEN Info_Panel SHALL отображать иконку по умолчанию
4. WHEN App_Name превышает 30 символов, THEN Info_Panel SHALL усекать текст с добавлением многоточия

### Requirement 2: Извлечение информации о Windows приложениях

**User Story:** Как система, я должна получать информацию об активном окне Windows, чтобы отображать её пользователю.

#### Acceptance Criteria

1. THE Window_Monitor SHALL использовать Windows API (win32gui.GetForegroundWindow) для определения Active_Window
2. WHEN Active_Window определено, THE Window_Monitor SHALL извлекать заголовок окна через win32gui.GetWindowText
3. WHEN Active_Window определено, THE Window_Monitor SHALL извлекать путь к исполняемому файлу через win32process и psutil
4. WHEN путь к исполняемому файлу получен, THE Window_Monitor SHALL извлекать App_Icon через win32gui.ExtractIconEx или win32ui
5. IF извлечение App_Icon завершается ошибкой, THEN Window_Monitor SHALL возвращать None для иконки

### Requirement 3: Отображение горячих клавиш

**User Story:** Как пользователь, я хочу видеть текущие горячие клавиши в окне записи, чтобы не забывать, как управлять приложением.

#### Acceptance Criteria

1. WHEN Floating_Window отображается, THEN Info_Panel SHALL показывать две кнопки с горячими клавишами
2. THE Info_Panel SHALL отображать кнопку "Record [hotkey]" с текущей горячей клавишей записи из Config_Manager
3. THE Info_Panel SHALL отображать кнопку "Close Esc" с клавишей отмены
4. WHEN горячая клавиша в Config_Manager изменяется, THEN Hotkey_Display SHALL обновляться автоматически в течение 100ms

### Requirement 4: Форматирование горячих клавиш

**User Story:** Как пользователь, я хочу видеть горячие клавиши в понятном формате, чтобы легко их запомнить.

#### Acceptance Criteria

1. WHEN горячая клавиша содержит модификатор "ctrl", THEN Hotkey_Display SHALL отображать "Ctrl+"
2. WHEN горячая клавиша содержит модификатор "alt", THEN Hotkey_Display SHALL отображать "Alt+"
3. WHEN горячая клавиша содержит модификатор "shift", THEN Hotkey_Display SHALL отображать "Shift+"
4. WHEN горячая клавиша является "space", THEN Hotkey_Display SHALL отображать "⎵Space"
5. WHEN горячая клавиша является функциональной клавишей (f1-f12), THEN Hotkey_Display SHALL отображать её в верхнем регистре (F1-F12)
6. WHEN горячая клавиша является буквой, THEN Hotkey_Display SHALL отображать её в верхнем регистре

### Requirement 5: Визуальный дизайн панели

**User Story:** Как пользователь, я хочу, чтобы информационная панель гармонично вписывалась в дизайн приложения, чтобы интерфейс выглядел целостно.

#### Acceptance Criteria

1. THE Info_Panel SHALL иметь темный фон, соответствующий цветовой схеме Floating_Window
2. THE Info_Panel SHALL быть отделена от основного контента горизонтальной линией толщиной 1px
3. THE Info_Panel SHALL иметь высоту 40px
4. THE Info_Panel SHALL использовать padding 8px по горизонтали и 6px по вертикали
5. WHEN App_Icon отображается, THEN она SHALL иметь размер 20x20 пикселей
6. THE Info_Panel SHALL использовать шрифт размером 11px для текста
7. THE Info_Panel SHALL использовать цвет текста #E0E0E0 для основного текста
8. THE Info_Panel SHALL использовать цвет текста #A0A0A0 для вторичного текста (горячих клавиш)

### Requirement 6: Компоновка элементов панели

**User Story:** Как пользователь, я хочу, чтобы информация в панели была организована логично, чтобы быстро находить нужные элементы.

#### Acceptance Criteria

1. THE Info_Panel SHALL использовать горизонтальный layout с выравниванием элементов по краям
2. WHEN отображается информация о приложении, THEN App_Icon и App_Name SHALL быть выровнены по левому краю
3. WHEN отображаются горячие клавиши, THEN они SHALL быть выровнены по правому краю
4. THE App_Icon SHALL иметь отступ 4px справа от App_Name
5. THE горячие клавиши SHALL иметь отступ 12px между собой

### Requirement 7: Интеграция с существующей системой

**User Story:** Как разработчик, я хочу, чтобы новая функция интегрировалась с существующим кодом, чтобы не нарушать работу приложения.

#### Acceptance Criteria

1. THE Info_Panel SHALL быть добавлена в FloatingWindow как дочерний виджет
2. THE Info_Panel SHALL не влиять на размер или позиционирование WaveformWidget
3. THE Window_Monitor SHALL запускаться при инициализации FloatingWindow
4. THE Window_Monitor SHALL останавливаться при закрытии FloatingWindow
5. WHEN происходит ошибка в Window_Monitor, THEN она SHALL логироваться через ErrorLogger, но не прерывать работу приложения

### Requirement 8: Производительность и ресурсы

**User Story:** Как пользователь, я хочу, чтобы отображение информации о приложении не замедляло работу системы, чтобы запись оставалась плавной.

#### Acceptance Criteria

1. THE Window_Monitor SHALL проверять Active_Window не чаще одного раза в 200ms
2. THE извлечение App_Icon SHALL выполняться асинхронно, чтобы не блокировать UI поток
3. THE Window_Monitor SHALL кэшировать App_Icon для каждого уникального приложения
4. WHEN кэш App_Icon превышает 50 записей, THEN Window_Monitor SHALL удалять наименее используемые записи

### Requirement 9: Кроссплатформенная совместимость

**User Story:** Как разработчик, я хочу подготовить архитектуру для поддержки других платформ, чтобы в будущем расширить функциональность.

#### Acceptance Criteria

1. THE Window_Monitor SHALL быть реализован как абстрактный базовый класс с методами get_active_window_info()
2. THE WindowsWindowMonitor SHALL быть конкретной реализацией для Windows
3. THE Window_Monitor SHALL автоматически выбирать правильную реализацию на основе platform.system()
4. WHERE платформа не Windows, THE Window_Monitor SHALL возвращать заглушку с сообщением "Unsupported platform"
