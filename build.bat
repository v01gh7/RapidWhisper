@echo off
chcp 65001 >nul
echo ========================================
echo   Сборка RapidWhisper в .exe
echo ========================================
echo.

echo [1/4] Проверка PyInstaller...
uv pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller не установлен. Устанавливаю...
    uv pip install pyinstaller
) else (
    echo PyInstaller уже установлен
)
echo.

echo [2/4] Сохранение ваших конфигураций...
if exist config.jsonc.backup del config.jsonc.backup
if exist secrets.json.backup del secrets.json.backup

if exist config.jsonc (
    echo Сохраняю текущий config.jsonc в config.jsonc.backup
    copy config.jsonc config.jsonc.backup >nul
    echo Ваш config.jsonc сохранен
)

if exist secrets.json (
    echo Сохраняю текущий secrets.json в secrets.json.backup
    copy secrets.json secrets.json.backup >nul
    echo Ваш secrets.json сохранен
)
echo.

echo [3/4] Очистка и сборка...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Очистка завершена
echo.

echo Сборка .exe файла...
echo Включаются:
echo   - Иконки (public/icons/*.svg, *.png)
echo   - Промпты форматирования (config/prompts/*.txt)
echo   - Основная иконка (public/RapidWhisper.ico)
echo.
echo НЕ включаются:
echo   - config.jsonc (создается в %%APPDATA%%\RapidWhisper)
echo   - secrets.json (создается в %%APPDATA%%\RapidWhisper)
echo.

uv run pyinstaller RapidWhisper.spec --clean
echo.

echo [4/4] Восстановление ваших конфигураций...
if exist config.jsonc.backup (
    echo Восстанавливаю ваш config.jsonc
    copy config.jsonc.backup config.jsonc >nul
    del config.jsonc.backup
    echo Ваш config.jsonc восстановлен
)

if exist secrets.json.backup (
    echo Восстанавливаю ваш secrets.json
    copy secrets.json.backup secrets.json >nul
    del secrets.json.backup
    echo Ваш secrets.json восстановлен
)
echo.

if exist "dist\RapidWhisper.exe" (
    goto :success
) else (
    goto :error
)

:success
echo ========================================
echo   Сборка завершена успешно!
echo ========================================
echo.
echo Файл: dist\RapidWhisper.exe
echo.
echo ВАЖНО: 
echo   - В .exe НЕТ config.jsonc и secrets.json
echo   - Настройки сохраняются в %%APPDATA%%\RapidWhisper\
echo   - При первом запуске создаются дефолтные конфиги
echo   - Пользователь настраивает через окно настроек
echo.
echo Включено в сборку:
echo   - Иконки для UI (public/icons/)
echo   - Промпты форматирования (config/prompts/)
echo   - Переводы интерфейса (utils/translations/)
echo   - Основная иконка приложения
echo.
echo Для распространения нужен только:
echo   - dist\RapidWhisper.exe
echo.
echo Примечание: Предупреждение "tzdata not found" можно игнорировать.
echo.
goto :end

:error
echo ========================================
echo   Сборка завершилась с ошибкой
echo ========================================
echo.
echo Проверьте логи выше для деталей
echo.
goto :end

:end
pause
