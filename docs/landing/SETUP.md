# Настройка лендинга RapidWhisper

## 🔗 Настройка ссылок на GitHub

После создания репозитория на GitHub, замените `V01GH7` на ваш GitHub username во всех файлах:

### Файлы для обновления:

1. **index.html** - главная страница
2. **docs.html** - страница документации
3. **README.md** - документация лендинга

### Быстрая замена (все файлы):

**Windows (PowerShell):**
```powershell
cd docs/landing
$username = "ваш-github-username"
(Get-Content index.html) -replace 'V01GH7', $username | Set-Content index.html
(Get-Content docs.html) -replace 'V01GH7', $username | Set-Content docs.html
(Get-Content README.md) -replace 'V01GH7', $username | Set-Content README.md
```

**macOS/Linux:**
```bash
cd docs/landing
USERNAME="ваш-github-username"
sed -i '' "s/V01GH7/$USERNAME/g" index.html
sed -i '' "s/V01GH7/$USERNAME/g" docs.html
sed -i '' "s/V01GH7/$USERNAME/g" README.md
```

**Или вручную:**
Найдите и замените во всех файлах:
- `V01GH7` → ваш GitHub username (с учетом регистра)
- `V01GH7` → ваш GitHub username (lowercase)

## 📦 Формат ссылок на скачивание

Ссылки используют специальный формат GitHub для автоматического скачивания последнего релиза:

```
https://github.com/USERNAME/rapidwhisper/releases/latest/download/FILENAME
```

### Текущие ссылки:

- **Windows**: `https://github.com/V01GH7/rapidwhisper/releases/latest/download/RapidWhisper.exe`
- **macOS**: `https://github.com/V01GH7/rapidwhisper/releases/latest/download/RapidWhisper-macOS.dmg`
- **Linux**: `https://github.com/V01GH7/rapidwhisper/releases/latest/download/RapidWhisper`

## 🚀 Создание релиза

### Вариант 1: Через GitHub Actions (рекомендуется)

1. Перейдите в GitHub → Actions
2. Выберите workflow "Build RapidWhisper"
3. Нажмите "Run workflow"
4. Дождитесь завершения сборки
5. Перейдите в Releases
6. Найдите созданный draft release
7. Отредактируйте описание и опубликуйте

### Вариант 2: Вручную

1. Соберите приложения для всех платформ
2. Перейдите в GitHub → Releases → "Create a new release"
3. Создайте тег (например, `v1.0.0`)
4. Загрузите файлы:
   - `RapidWhisper.exe` (Windows)
   - `RapidWhisper-macOS.dmg` (macOS)
   - `RapidWhisper` (Linux binary)
5. Опубликуйте релиз

## ✅ Проверка ссылок

После публикации релиза проверьте, что ссылки работают:

1. Откройте `index.html` в браузере
2. Нажмите на кнопки скачивания
3. Убедитесь, что файлы скачиваются

### Если ссылки не работают:

- Убедитесь, что релиз опубликован (не draft)
- Проверьте, что имена файлов совпадают точно
- Проверьте, что username указан правильно

## 🌐 Деплой лендинга

### GitHub Pages

1. Перейдите в Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` или `master`
4. Folder: `/docs/landing` или `/docs` (если переместите landing в корень docs)
5. Сохраните

Сайт будет доступен по адресу:
```
https://V01GH7.github.io/rapidwhisper/
```

### Netlify

1. Перетащите папку `docs/landing` на Netlify
2. Или подключите GitHub репозиторий
3. Build directory: `docs/landing`

### Vercel

```bash
cd docs/landing
vercel
```

## 📝 Обновление контента

### Изменить описание фич:

Отредактируйте секцию `.features-grid` в `index.html`

### Добавить скриншоты:

1. Создайте папку `docs/landing/images/`
2. Добавьте изображения
3. Обновите HTML:
```html
<img src="images/screenshot.png" alt="RapidWhisper">
```

### Изменить цвета:

Отредактируйте CSS переменные в `styles.css`:
```css
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
}
```

## 🔧 Дополнительные настройки

### Добавить Google Analytics:

Добавьте перед закрывающим `</head>`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Добавить favicon:

```html
<link rel="icon" type="image/png" href="favicon.png">
```

### Добавить Open Graph теги (для соцсетей):

```html
<meta property="og:title" content="RapidWhisper - Voice to Text">
<meta property="og:description" content="Fast, accurate speech-to-text transcription">
<meta property="og:image" content="https://yourdomain.com/og-image.png">
<meta property="og:url" content="https://yourdomain.com">
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте, что все ссылки обновлены
2. Убедитесь, что релиз опубликован
3. Проверьте консоль браузера на ошибки
4. Создайте issue на GitHub

---

**Готово!** После настройки ваш лендинг будет автоматически скачивать последние версии из GitHub Releases.
