"""
Rich Clipboard Manager для вставки форматированного текста.

Поддерживает вставку HTML в буфер обмена для Word, Google Docs, LibreOffice.
"""

import win32clipboard
import win32con
from typing import Optional
from utils.logger import get_logger

logger = get_logger()


class RichClipboardManager:
    """
    Менеджер буфера обмена с поддержкой форматированного текста.
    
    Позволяет вставлять HTML в буфер обмена, который автоматически
    применяется как форматирование в Word, Google Docs, LibreOffice.
    """
    
    @staticmethod
    def copy_html_to_clipboard(html: str, plain_text: str) -> bool:
        """
        Копирует HTML в буфер обмена с fallback на обычный текст.
        
        Args:
            html: HTML текст с форматированием
            plain_text: Обычный текст (fallback для приложений без HTML)
        
        Returns:
            True если копирование успешно, False в случае ошибки
        """
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            
            # Добавить обычный текст (для совместимости)
            win32clipboard.SetClipboardText(plain_text, win32con.CF_UNICODETEXT)
            
            # Добавить HTML (для Word, Google Docs, LibreOffice)
            # Формат HTML для буфера обмена Windows
            html_clipboard = RichClipboardManager._create_html_clipboard_format(html)
            win32clipboard.SetClipboardData(
                win32clipboard.RegisterClipboardFormat("HTML Format"),
                html_clipboard.encode('utf-8')
            )
            
            win32clipboard.CloseClipboard()
            logger.info("HTML скопирован в буфер обмена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка копирования HTML в буфер обмена: {e}")
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return False
    
    @staticmethod
    def _create_html_clipboard_format(html: str) -> str:
        """
        Создает HTML в формате буфера обмена Windows.
        
        Windows требует специальный формат с заголовками для HTML.
        
        Args:
            html: HTML контент
        
        Returns:
            HTML в формате буфера обмена Windows
        """
        # Обернуть HTML в полный документ
        html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; font-size: 11pt; }}
h1 {{ font-size: 18pt; font-weight: bold; margin-top: 12pt; margin-bottom: 6pt; }}
h2 {{ font-size: 14pt; font-weight: bold; margin-top: 10pt; margin-bottom: 5pt; }}
h3 {{ font-size: 12pt; font-weight: bold; margin-top: 8pt; margin-bottom: 4pt; }}
ul, ol {{ margin-top: 6pt; margin-bottom: 6pt; }}
li {{ margin-bottom: 3pt; }}
strong {{ font-weight: bold; }}
em {{ font-style: italic; }}
</style>
</head>
<body>
{html}
</body>
</html>"""
        
        # CRITICAL: Создать заголовок с временными значениями для вычисления его длины
        temp_header = """Version:0.9
StartHTML:0000000000
EndHTML:0000000000
StartFragment:0000000000
EndFragment:0000000000
"""
        
        # Длина заголовка в байтах
        header_length = len(temp_header.encode('utf-8'))
        
        # Вычислить смещения ПОСЛЕ заголовка
        start_html = header_length + html_doc.find('<html>')
        end_html = header_length + html_doc.find('</html>') + 7
        start_fragment = header_length + html_doc.find('<body>') + 6
        end_fragment = header_length + html_doc.find('</body>')
        
        # Создать правильный заголовок с вычисленными смещениями
        header = f"""Version:0.9
StartHTML:{start_html:010d}
EndHTML:{end_html:010d}
StartFragment:{start_fragment:010d}
EndFragment:{end_fragment:010d}
"""
        
        return header + html_doc
    
    @staticmethod
    def copy_plain_to_clipboard(text: str) -> bool:
        """
        Копирует обычный текст в буфер обмена.
        
        Args:
            text: Текст для копирования
        
        Returns:
            True если копирование успешно, False в случае ошибки
        """
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            logger.error(f"Ошибка копирования текста в буфер обмена: {e}")
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return False
