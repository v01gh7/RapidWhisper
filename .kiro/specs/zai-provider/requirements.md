# Requirements Document: Z.AI Provider Integration

## Introduction

Данный документ описывает требования к интеграции нового AI провайдера Z.AI в приложение RapidWhisper. Z.AI представляет собой прокси-сервис, предоставляющий доступ к GLM-моделям через Anthropic SDK API. Интеграция позволит пользователям использовать GLM-модели через альтернативный API endpoint с улучшенной производительностью.

## Glossary

- **Z.AI**: Прокси-сервис, предоставляющий доступ к GLM-моделям через Anthropic-совместимый API
- **Provider**: AI провайдер для транскрипции и обработки текста (openai, groq, glm, custom, zai)
- **TranscriptionClient**: Универсальный клиент для транскрипции аудио, использующий OpenAI SDK
- **ZAIClient**: Новый клиент для работы с Z.AI через Anthropic SDK
- **Config**: Класс конфигурации приложения, хранящий настройки провайдеров и API ключи
- **FormattingModule**: Модуль форматирования текста через AI
- **Anthropic SDK**: Python SDK для работы с Anthropic API (используется Z.AI)
- **GLM_API_KEY**: API ключ для доступа к GLM и Z.AI сервисам
- **Base_URL**: URL endpoint для API провайдера

## Requirements

### Requirement 1: Z.AI Provider Configuration

**User Story:** Как пользователь, я хочу выбрать Z.AI в качестве AI провайдера, чтобы использовать GLM-модели через альтернативный API endpoint.

#### Acceptance Criteria

1. WHEN пользователь выбирает провайдер "zai" в настройках, THEN THE System SHALL использовать Z.AI API endpoint `https://api.z.ai/api/anthropic`
2. WHEN провайдер установлен как "zai", THEN THE System SHALL использовать GLM_API_KEY для аутентификации
3. WHEN провайдер "zai" выбран, THEN THE System SHALL использовать модель `GLM-4.7` по умолчанию
4. WHEN провайдер "zai" выбран, THEN THE System SHALL устанавливать таймаут запросов в 130 секунд
5. THE Config SHALL валидировать что "zai" является допустимым значением для ai_provider

### Requirement 2: Anthropic SDK Integration

**User Story:** Как разработчик, я хочу использовать Anthropic SDK для взаимодействия с Z.AI, чтобы обеспечить совместимость с Anthropic API.

#### Acceptance Criteria

1. WHEN ZAIClient инициализируется, THEN THE System SHALL создавать экземпляр Anthropic клиента с base_url `https://api.z.ai/api/anthropic`
2. WHEN ZAIClient отправляет запрос, THEN THE System SHALL использовать метод `messages.create()` из Anthropic SDK
3. WHEN ZAIClient создается, THEN THE System SHALL устанавливать timeout в 130.0 секунд
4. THE System SHALL устанавливать зависимость `anthropic` в requirements.txt

### Requirement 3: Text Processing Support

**User Story:** Как пользователь, я хочу использовать Z.AI для постобработки и форматирования текста, чтобы улучшить качество транскрипции.

#### Acceptance Criteria

1. WHEN постобработка включена и провайдер установлен как "zai", THEN THE System SHALL использовать ZAIClient для обработки текста
2. WHEN форматирование включено и провайдер установлен как "zai", THEN THE FormattingModule SHALL использовать ZAIClient для форматирования
3. WHEN ZAIClient обрабатывает текст, THEN THE System SHALL отправлять запрос с параметрами model, max_tokens, messages
4. WHEN ZAIClient получает ответ, THEN THE System SHALL извлекать текст из response.content[0].text

### Requirement 4: Audio Transcription Support (Optional)

**User Story:** Как пользователь, я хочу использовать Z.AI для транскрипции аудио, если эта функция поддерживается сервисом.

#### Acceptance Criteria

1. IF Z.AI поддерживает транскрипцию аудио, THEN THE ZAIClient SHALL реализовать метод transcribe_audio()
2. IF Z.AI не поддерживает транскрипцию аудио, THEN THE System SHALL показывать понятное сообщение об ошибке
3. WHEN пользователь выбирает "zai" для транскрипции, THEN THE System SHALL проверять поддержку этой функции

### Requirement 5: UI Settings Integration

**User Story:** Как пользователь, я хочу видеть Z.AI в списке доступных провайдеров в настройках, чтобы легко переключаться между провайдерами.

#### Acceptance Criteria

1. WHEN пользователь открывает окно настроек, THEN THE System SHALL отображать "Z.AI" в выпадающем списке провайдеров
2. WHEN пользователь выбирает "Z.AI", THEN THE UI SHALL показывать что используется GLM_API_KEY
3. WHEN пользователь выбирает "Z.AI", THEN THE UI SHALL отображать ссылку на документацию Z.AI
4. WHEN пользователь выбирает "Z.AI", THEN THE UI SHALL показывать модель по умолчанию "GLM-4.7"

### Requirement 6: Error Handling

**User Story:** Как пользователь, я хочу получать понятные сообщения об ошибках при работе с Z.AI, чтобы быстро решать проблемы.

#### Acceptance Criteria

1. WHEN API ключ отсутствует для провайдера "zai", THEN THE System SHALL выбрасывать InvalidAPIKeyError с указанием провайдера
2. WHEN запрос к Z.AI превышает таймаут, THEN THE System SHALL выбрасывать APITimeoutError с указанием таймаута 130 секунд
3. WHEN происходит ошибка аутентификации, THEN THE System SHALL выбрасывать APIAuthenticationError с сообщением о проверке GLM_API_KEY
4. WHEN происходит ошибка сети, THEN THE System SHALL выбрасывать APINetworkError с понятным описанием
5. WHEN модель не найдена, THEN THE System SHALL выбрасывать ModelNotFoundError с указанием модели и провайдера

### Requirement 7: Configuration File Updates

**User Story:** Как пользователь, я хочу чтобы настройки Z.AI сохранялись в конфигурационных файлах, чтобы они сохранялись между запусками приложения.

#### Acceptance Criteria

1. WHEN пользователь выбирает провайдер "zai", THEN THE System SHALL сохранять значение в config.jsonc
2. WHEN пользователь вводит GLM_API_KEY, THEN THE System SHALL сохранять его в secrets.json
3. WHEN пользователь выбирает кастомную модель для "zai", THEN THE System SHALL сохранять её в config.jsonc
4. THE System SHALL загружать настройки "zai" при старте приложения

### Requirement 8: Backward Compatibility

**User Story:** Как пользователь, я хочу чтобы добавление Z.AI не нарушало работу существующих провайдеров, чтобы я мог продолжать использовать OpenAI, Groq или GLM.

#### Acceptance Criteria

1. WHEN Z.AI добавлен в систему, THEN THE System SHALL продолжать поддерживать провайдеры openai, groq, glm, custom
2. WHEN пользователь использует существующий провайдер, THEN THE System SHALL работать без изменений
3. WHEN происходит миграция конфигурации, THEN THE System SHALL сохранять все существующие настройки
4. THE System SHALL не изменять поведение TranscriptionClient для существующих провайдеров

### Requirement 9: API Response Handling

**User Story:** Как разработчик, я хочу корректно обрабатывать ответы от Z.AI API, чтобы извлекать текст в правильном формате.

#### Acceptance Criteria

1. WHEN ZAIClient получает ответ от API, THEN THE System SHALL проверять наличие поля content в ответе
2. WHEN ответ содержит content, THEN THE System SHALL извлекать текст из первого элемента массива content
3. WHEN ответ не содержит content, THEN THE System SHALL выбрасывать APIResponseError
4. WHEN текст успешно извлечен, THEN THE System SHALL возвращать строку с обработанным текстом

### Requirement 10: Testing and Validation

**User Story:** Как разработчик, я хочу иметь тесты для Z.AI интеграции, чтобы гарантировать корректную работу функционала.

#### Acceptance Criteria

1. THE System SHALL иметь unit тесты для ZAIClient инициализации
2. THE System SHALL иметь unit тесты для обработки текста через Z.AI
3. THE System SHALL иметь unit тесты для обработки ошибок Z.AI
4. THE System SHALL иметь integration тесты для проверки взаимодействия с Config и FormattingModule
