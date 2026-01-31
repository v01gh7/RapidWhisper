# Web Applications Support in Browsers

## Overview

RapidWhisper automatically detects web applications running in browsers and applies appropriate formatting to transcribed text.

## How It Works

1. **Browser Detection**: System checks if the active application is a browser
2. **Tab Title Analysis**: Reads the active browser tab title
3. **Keyword Matching**: Searches for specific keywords in the title
4. **Format Application**: Applies the corresponding formatting

## Supported Browsers

- Google Chrome
- Mozilla Firefox
- Microsoft Edge
- Opera
- Brave
- Vivaldi
- Safari

## Supported Web Applications

### 📝 Google Services → `word` format

| Application | English | Russian |
|-------------|---------|---------|
| Documents | Google Docs | Google Документы |
| Spreadsheets | Google Sheets | Google Таблицы |
| Presentations | Google Slides | Google Презентации |
| Forms | Google Forms | Google Формы |
| Notes | Google Keep | Google Keep |

**Example titles:**
- ✅ "My document - Google Docs"
- ✅ "Мой документ - Google Документы"
- ✅ "Budget 2024 - Google Sheets"
- ✅ "Бюджет 2024 - Google Таблицы"

---

### 💼 Microsoft Office Online → `word` format

| Application | Keywords |
|-------------|----------|
| Word Online | microsoft word online |
| Excel Online | microsoft excel online |
| PowerPoint Online | microsoft powerpoint online |
| Office 365 | office 365 |
| Office Online | office online |

**Example titles:**
- ✅ "Document1 - Microsoft Word Online"
- ✅ "Spreadsheet - Microsoft Excel Online"
- ✅ "Report - Office 365"

---

### 🤝 Collaboration Tools → `word` format

| Application | Description | Keywords |
|-------------|-------------|----------|
| Dropbox Paper | Collaborative editing | dropbox paper |
| Quip | Team documents | quip |
| Coda.io | All-in-one platform | coda.io |
| Airtable | Spreadsheet + database | airtable |

**Example titles:**
- ✅ "Project Notes - Dropbox Paper"
- ✅ "Team Doc - Quip"
- ✅ "My Workspace - Coda.io"

---

### 📊 Zoho Office Suite → `word` format

| Application | Keywords |
|-------------|----------|
| Zoho Writer | zoho writer |
| Zoho Sheet | zoho sheet |
| Zoho Show | zoho show |

**Example titles:**
- ✅ "Document - Zoho Writer"
- ✅ "Spreadsheet - Zoho Sheet"

---

### 📔 Note-Taking & Knowledge Management

| Application | Format | Keywords |
|-------------|--------|----------|
| Notion | `notion` | notion, notion.so |
| Obsidian Publish | `obsidian` | obsidian publish |

**Example titles:**
- ✅ "My Page - Notion" → `notion` format
- ✅ "Workspace - Notion.so" → `notion` format
- ✅ "My Notes - Obsidian Publish" → `obsidian` format

---

### ✍️ Markdown Editors → `markdown` format

| Application | Description | Keywords |
|-------------|-------------|----------|
| HackMD | Collaborative markdown | hackmd |
| StackEdit | In-browser editor | stackedit |
| Dillinger | Online editor | dillinger |
| Typora Online | Minimalist editor | typora online |
| GitHub.dev | GitHub web editor | github.dev |
| GitLab | GitLab web IDE | gitlab |
| Gitpod | Cloud dev environment | gitpod |

**Example titles:**
- ✅ "README.md - HackMD"
- ✅ "Notes - StackEdit"
- ✅ "Code - GitHub.dev"
- ✅ "Project - GitLab"

---

## Configuration

### Enabling Formatting for Web Apps

1. Open **Settings** → **Processing**
2. Enable **"Formatting"**
3. Add required formats to the applications list:
   - `word` - for Google Docs, Office Online, etc.
   - `notion` - for Notion
   - `obsidian` - for Obsidian Publish
   - `markdown` - for markdown editors

### Example Configuration

```env
FORMATTING_ENABLED=true
FORMATTING_PROVIDER=groq
FORMATTING_MODEL=llama-3.3-70b-versatile
FORMATTING_APPLICATIONS=word,notion,obsidian,markdown
```

## Custom Prompts for Web Apps

You can configure individual prompts for each format:

### For Google Docs/Office Online (word)
```
Format this text for online document editors with:
- Clear paragraph structure
- Proper headings hierarchy
- Bulleted and numbered lists
- Professional formatting
```

### For Notion (notion)
```
Format this text for Notion with:
- Use ## for main headings, ### for subheadings
- Create toggle lists for detailed sections
- Use callout blocks for important notes
```

### For Markdown Editors (markdown)
```
Format this text as clean Markdown with:
- Standard # heading syntax
- Proper list formatting (-, *, 1.)
- Code blocks with ``` when needed
```

## Debugging

### Checking Web App Detection

Logs show the detection process:

```
🔍 Determining active window...
📱 Active window:
  - Process: chrome.exe
  - Title: My document - Google Docs
🌐 Browser detected: chrome.exe
🔎 Checking tab title for web applications...
🌐 Web application detected: 'google docs' → format 'word'
✅ Web application found: word
```

### If Web App Is Not Detected

1. **Check tab title**: Ensure the title contains keywords
2. **Check applications list**: Ensure the corresponding format is added in settings
3. **Check logs**: Look for "Browser detected" and "Checking tab title" messages

### Adding a New Web Application

If you want to add support for a new web application, edit `services/formatting_module.py`:

```python
BROWSER_TITLE_MAPPINGS = {
    "word": [
        # ... existing patterns ...
        "your-app-name",  # Add keyword
    ],
}
```

## Limitations

1. **Title Dependency**: Detection only works if the tab title contains keywords
2. **Tab Switching**: System tracks title changes with 200ms interval
3. **Language Support**: English and Russian titles are supported

## FAQ

**Q: Does this work with private/incognito tabs?**
A: Yes, the system detects the title regardless of browser mode.

**Q: Can I add support for other languages?**
A: Yes, add corresponding keywords to `BROWSER_TITLE_MAPPINGS`.

**Q: What if I have multiple Google Docs tabs open?**
A: The system only detects the active tab (the one currently in focus).

**Q: Does this work with mobile browsers?**
A: No, the feature only works on Windows desktop versions.

## Feedback

If you want to add support for a new web application or found an issue, create an issue on GitHub.
