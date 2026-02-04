# Implementation Plan: Z.AI Provider Integration

## Overview

Данный план описывает пошаговую реализацию интеграции Z.AI провайдера в RapidWhisper. Z.AI будет добавлен как новый провайдер рядом с существующими (openai, groq, glm, custom), используя Anthropic SDK вместо OpenAI SDK.

**Ключевые точки интеграции:**
- `core/config.py` - добавить "zai" в валидные провайдеры
- `services/transcription_client.py` - расширить для поддержки Anthropic SDK
- `ui/settings_window.py` - добавить "zai" в UI (3 комбобокса)
- `services/formatting_module.py` - уже использует TranscriptionClient, работает автоматически

## Tasks

- [x] 1. Setup dependencies
  - Добавить `anthropic>=0.18.0` в requirements.txt
  - Добавить `anthropic>=0.18.0` в requirements-windows.txt
  - Добавить `anthropic>=0.18.0` в requirements-macos.txt
  - Добавить `anthropic>=0.18.0` в requirements-linux.txt
  - _Requirements: 2.4_

- [x] 2. Extend TranscriptionClient to support Anthropic SDK
  - [x] 2.1 Add Anthropic client initialization in __init__
    - Импортировать `from anthropic import Anthropic`
    - Добавить `self.anthropic_client = None` в __init__
    - Если provider == "zai", создать Anthropic клиент вместо OpenAI
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.3_
  
  - [x] 2.2 Update post_process_text() to support Anthropic API
    - Добавить проверку: если provider == "zai", использовать anthropic_client
    - Для Z.AI вызывать `client.messages.create()` вместо `client.chat.completions.create()`
    - Извлекать текст из `response.content[0].text` для Anthropic
    - Сохранить существующую логику для OpenAI-based провайдеров
    - _Requirements: 2.2, 3.3, 3.4, 9.1, 9.2, 9.4_
  
  - [x] 2.3 Add error handling for Anthropic SDK exceptions
    - Импортировать Anthropic exceptions
    - Добавить try-except блоки для Anthropic ошибок в post_process_text()
    - Пробрасывать Anthropic ошибки как есть (не преобразовывать)
    - _Requirements: 6.2, 6.3, 6.4, 9.3_
  
  - [x] 2.4 Update transcribe_audio() documentation
    - Добавить комментарий что Z.AI не поддерживает транскрипцию аудио
    - Если provider == "zai" в transcribe_audio(), выбросить понятную ошибку
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 2.5 Write unit tests for Z.AI in TranscriptionClient
    - Тест инициализации с provider="zai"
    - Тест что transcribe_audio() выбрасывает NotImplementedError для "zai"
    - Тест post_process_text() с мокированным Anthropic client
    - Тест извлечения текста из response.content[0].text
    - Тест обработки Anthropic ошибок
    - _Requirements: 1.3, 1.4, 3.4, 4.1, 4.2, 6.2, 6.3, 6.4, 9.1, 9.3_


- [x] 3. Update Config class to support Z.AI
  - [x] 3.1 Add "zai" to valid providers list
    - В методе `validate()` обновить список valid_providers
    - Добавить проверку GLM_API_KEY для "zai"
    - _Requirements: 1.5, 1.2_
  
  - [x] 3.2 Update _get_api_key_for_provider() in main.py
    - Добавить case для "zai" который возвращает glm_api_key
    - _Requirements: 1.2_
  
  - [x] 3.3 Write unit tests for Config with Z.AI
    - Тест что Config.validate() принимает "zai" как валидный провайдер
    - Тест что Config.validate() требует GLM_API_KEY для "zai"
    - _Requirements: 1.5, 1.2_

- [x] 4. Update UI settings window
  - [x] 4.1 Add "zai" to main provider dropdown
    - В `_create_ai_provider_tab()` добавить "zai" в список провайдеров
    - _Requirements: 5.1_
  
  - [x] 4.2 Update _on_provider_changed() to handle "zai"
    - Добавить case для "zai" который подсвечивает glm_key_edit
    - _Requirements: 5.2_
  
  - [x] 4.3 Add "zai" to post-processing provider dropdown
    - В `_create_processing_tab()` добавить "zai" в список
    - _Requirements: 5.1_
  
  - [x] 4.4 Update _on_post_processing_provider_changed() for "zai"
    - Добавить case для "zai" с моделью "GLM-4.7"
    - _Requirements: 5.4_
  
  - [x] 4.5 Add "zai" to formatting provider dropdown
    - В `_create_formatting_tab()` добавить "zai" в список
    - _Requirements: 5.1_

- [x] 5. Update config examples
  - [x] 5.1 Add Z.AI comments to config.jsonc.example
    - Добавить комментарий о Z.AI в секцию ai_provider
    - _Requirements: 7.1, 7.3_
  
  - [x] 5.2 Add Z.AI comments to secrets.json.example
    - Добавить комментарий что GLM ключ используется для Z.AI
    - _Requirements: 7.2_

- [x] 6. Integration testing
  - [x] 6.1 Test Z.AI with post-processing
    - Integration тест: постобработка с provider="zai"
    - _Requirements: 3.1_
  
  - [x] 6.2 Test Z.AI with formatting
    - Integration тест: форматирование с provider="zai"
    - _Requirements: 3.2_
  
  - [x] 6.3 Test error handling for Z.AI
    - Тесты для всех типов ошибок Z.AI
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 4.2_
  
  - [x] 6.4 Test backward compatibility
    - Запустить существующие тесты для других провайдеров
    - _Requirements: 8.1, 8.2, 8.4_

- [x] 7. Property-based testing
  - [x] 7.1 Write property test for Z.AI initialization
    - Property 1: ZAIClient Initialization Correctness
    - _Validates: Requirements 1.1, 1.2, 2.1_
  
  - [x] 7.2 Write property test for Anthropic API request structure
    - Property 4: Anthropic API Request Structure
    - _Validates: Requirements 2.2, 3.3_
  
  - [x] 7.3 Write property test for response parsing
    - Property 5: Response Parsing Correctness
    - _Validates: Requirements 3.4, 9.2, 9.4_
  
  - [x] 7.4 Write property test for error handling
    - Property 9: Error Handling Completeness
    - _Validates: Requirements 6.2, 6.3, 6.4, 6.5, 9.1, 9.3_

- [x] 8. Manual testing
  - [x] 8.1 Test UI integration
    - Проверить что "zai" появляется во всех 3 комбобоксах
    - Проверить подсветку GLM_API_KEY поля
    - Проверить сохранение настроек
  
  - [x] 8.2 Test post-processing with Z.AI
    - Выполнить транскрипцию с постобработкой через Z.AI
    - Проверить логи
  
  - [x] 8.3 Test formatting with Z.AI
    - Выполнить транскрипцию с форматированием через Z.AI
  
  - [x] 8.4 Test error scenarios
    - Проверить ошибки без API ключа
    - Проверить ошибку при попытке транскрипции
  
  - [x] 8.5 Test backward compatibility
    - Проверить что все существующие провайдеры работают

- [x] 9. Documentation
  - [x] 9.1 Update README.md
    - Добавить Z.AI в список провайдеров
    - Описать особенности Z.AI
  
  - [x] 9.2 Update docs/INDEX.md
    - Добавить информацию о Z.AI
  
  - [x] 9.3 Add troubleshooting section
    - Добавить раздел о типичных ошибках Z.AI

- [-] 10. Final checkpoint
  - [ ] 10.1 Run all tests
    - Запустить pytest для всех тестов
  
  - [ ] 10.2 Check code quality
    - Запустить black и ruff
  
  - [ ] 10.3 Verify all requirements
    - Проверить что все требования выполнены
  
  - [ ] 10.4 Clean up
    - Удалить TODO и debug код

## Notes

- **Hypothesis уже установлен** - не нужно добавлять
- **TranscriptionClient уже существует** - расширяем его
- **FormattingModule работает автоматически** - использует TranscriptionClient
- **3 комбобокса в UI** - AI Provider, Post-processing, Formatting
- **GLM_API_KEY для Z.AI** - не нужен отдельный ключ
- **Z.AI НЕ поддерживает транскрипцию** - только text processing
