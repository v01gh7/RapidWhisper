@echo off
echo ========================================
echo   Сборка RapidWhisper в .exe
echo ========================================
echo.

echo [1/5] Проверка PyInstaller...
uv pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller не установлен. Устанавливаю...
    uv pip install pyinstaller
) else (
    echo PyInstaller уже установлен
)
echo.

echo [2/5] Создание чистого .env для сборки...
if exist .env.backup del .env.backup
if exist .env (
    echo Сохраняю текущий .env в .env.backup
    copy .env .env.backup >nul
)

echo Создаю чистый .env без ключей...
(
echo # ============================================
echo # AI Provider Configuration ^(OPTIONAL^)
echo # ============================================
echo # AI provider for transcription
echo # Default: groq ^(free and fast!^)
echo # Options: openai, groq, glm
echo AI_PROVIDER=groq
echo.
echo # OpenAI API Key ^(for provider=openai^)
echo # Get from: https://platform.openai.com/api-keys
echo OPENAI_API_KEY=
echo.
echo # Groq API Key ^(for provider=groq^)
echo # Get from: https://console.groq.com/keys
echo GROQ_API_KEY=
echo.
echo # GLM API Key ^(for provider=glm^)
echo # Get from: https://open.bigmodel.cn/usercenter/apikeys
echo GLM_API_KEY=
echo.
echo # ============================================
echo # Application Settings ^(OPTIONAL^)
echo # ============================================
echo # Global hotkey for activating the application
echo # Default: ctrl+space
echo # Options: F1-F12, or combinations like ctrl+shift+r, ctrl+space
echo HOTKEY=ctrl+space
echo.
echo # Silence detection threshold ^(RMS value^)
echo # Default: 0.02
echo # Range: 0.01 - 0.1 ^(lower = more sensitive^)
echo SILENCE_THRESHOLD=0.02
echo.
echo # Silence duration before stopping recording ^(seconds^)
echo # Default: 1.5
echo # Range: 0.5 - 5.0
echo SILENCE_DURATION=1.5
echo.
echo # Auto-hide delay after displaying result ^(seconds^)
echo # Default: 2.5
echo # Range: 1.0 - 10.0
echo AUTO_HIDE_DELAY=2.5
) > .env

echo Чистый .env создан
echo.

echo [3/5] Очистка предыдущей сборки...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Очистка завершена
echo.

echo [4/5] Сборка .exe файла...
uv run pyinstaller RapidWhisper.spec --clean
echo.

echo [5/5] Восстановление вашего .env...
if exist .env.backup (
    echo Восстанавливаю ваш .env с ключами
    copy .env.backup .env >nul
    del .env.backup
    echo Ваш .env восстановлен
) else (
    echo Backup не найден, .env остался чистым
)
echo.

if exist dist\RapidWhisper.exe (
    echo ========================================
    echo   Сборка завершена успешно!
    echo ========================================
    echo.
    echo Файл: dist\RapidWhisper.exe
    echo.
    echo ВАЖНО: В .exe НЕТ ваших API ключей!
    echo Пользователи должны создать свой .env файл
    echo.
    echo Для распространения скопируйте:
    echo   - dist\RapidWhisper.exe
    echo   - .env.example
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
