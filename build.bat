@echo off
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

echo [2/4] Сохранение вашего .env...
if exist .env.backup del .env.backup
if exist .env (
    echo Сохраняю текущий .env в .env.backup
    copy .env .env.backup >nul
    echo Ваш .env сохранен
)
echo.

echo [3/4] Очистка и сборка...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Очистка завершена
echo.

echo Сборка .exe файла (без .env файлов)...
uv run pyinstaller RapidWhisper.spec --clean
echo.

echo [4/4] Восстановление вашего .env...
if exist .env.backup (
    echo Восстанавливаю ваш .env с ключами
    copy .env.backup .env >nul
    del .env.backup
    echo Ваш .env восстановлен
) else (
    echo Backup не найден
)
echo.

if exist dist\RapidWhisper.exe (
    echo ========================================
    echo   Сборка завершена успешно!
    echo ========================================
    echo.
    echo Файл: dist\RapidWhisper.exe
    echo.
    echo ВАЖНО: 
    echo   - В .exe НЕТ .env файлов
    echo   - Настройки сохраняются в %%APPDATA%%\RapidWhisper\.env
    echo   - При первом запуске пользователь увидит инструкцию
    echo   - Нужно будет установить API ключ через настройки
    echo.
    echo Для распространения нужен только:
    echo   - dist\RapidWhisper.exe
    echo.
) else (
    echo ========================================
    echo   Сборка завершилась с ошибкой
    echo ========================================
    echo.
    echo Проверьте логи выше для деталей
    echo.
)

pause
