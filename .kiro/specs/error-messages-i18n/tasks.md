# Implementation Plan: Error Messages Internationalization

## Overview

This plan implements internationalization for all user-facing error messages, notifications, and status messages in RapidWhisper. The implementation follows a phased approach to ensure backward compatibility while gradually migrating to the new i18n-based exception system.

## Tasks

- [x] 1. Enhance base exception classes with i18n support
  - [x] 1.1 Update RapidWhisperError base class
    - Add translation_key parameter to constructor
    - Add translation_params dict for parameter storage
    - Implement user_message property that calls i18n.t()
    - Preserve technical message for logging
    - Add backward compatibility for legacy constructor calls
    - _Requirements: 1.1, 1.2, 6.1, 6.4, 8.1_
  
  - [x] 1.2 Write property test for exception translation
    - **Property 1: Exception Message Translation**
    - **Validates: Requirements 1.1**
  
  - [x] 1.3 Write property test for parameter interpolation
    - **Property 2: Parameter Interpolation**
    - **Validates: Requirements 1.2, 6.2**
  
  - [x] 1.4 Write unit tests for backward compatibility
    - Test legacy exception creation (without translation_key)
    - Test mixed usage (old and new style)
    - _Requirements: 8.1_

- [x] 2. Add translation keys to translation files
  - [x] 2.1 Add error message keys to English translation file
    - Add all error messages under "errors" namespace
    - Include parameter placeholders (e.g., {provider}, {model})
    - Add API error messages
    - Add audio error messages
    - Add configuration error messages
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 2.2 Add error message keys to Russian translation file
    - Translate all English error messages to Russian
    - Maintain same parameter placeholders
    - Verify namespace structure matches English
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 2.3 Add error message keys to remaining 13 language files
    - Copy English translations as placeholders
    - Add TODO comments for future translation
    - Verify all files have same structure
    - _Requirements: 5.1, 5.5_
  
  - [x] 2.4 Write property test for translation completeness
    - **Property 6: Translation Completeness**
    - **Validates: Requirements 5.1**
  
  - [x] 2.5 Write property test for translation file structure
    - **Property 7: Translation File Structure Consistency**
    - **Validates: Requirements 5.3, 5.4, 5.5**
  
  - [x] 2.6 Write property test for parameter syntax validation
    - **Property 8: Parameter Syntax Validation**
    - **Validates: Requirements 5.2**

- [x] 3. Checkpoint - Verify translation infrastructure
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update API exception classes
  - [x] 4.1 Update APIAuthenticationError
    - Add translation_key="errors.api_authentication"
    - Add provider parameter
    - Update constructor to use new base class features
    - _Requirements: 2.1_
  
  - [x] 4.2 Update APINetworkError
    - Add translation_key="errors.api_network"
    - Add provider parameter
    - _Requirements: 2.2_
  
  - [x] 4.3 Update APITimeoutError
    - Add translation_key="errors.api_timeout"
    - Add provider and timeout parameters
    - _Requirements: 2.3_
  
  - [x] 4.4 Add ModelNotFoundError class
    - Create new exception class
    - Add translation_key="errors.model_not_found"
    - Add model and provider parameters
    - _Requirements: 2.5_
  
  - [x] 4.5 Update InvalidAPIKeyError
    - Add translation_key="errors.invalid_api_key"
    - Add provider parameter
    - _Requirements: 2.1_
  
  - [x] 4.6 Write unit tests for API exceptions
    - Test APIAuthenticationError with different providers
    - Test APINetworkError translation
    - Test APITimeoutError with timeout parameter
    - Test ModelNotFoundError with model and provider
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [x] 5. Update audio exception classes
  - [x] 5.1 Update MicrophoneUnavailableError
    - Add translation_key="errors.microphone_unavailable"
    - _Requirements: 1.1_
  
  - [x] 5.2 Update RecordingTooShortError
    - Add translation_key="errors.recording_too_short"
    - Add duration parameter
    - _Requirements: 1.2_
  
  - [x] 5.3 Update EmptyRecordingError
    - Add translation_key="errors.empty_recording"
    - _Requirements: 1.1_
  
  - [x] 5.4 Update AudioDeviceError
    - Add translation_key="errors.audio_device_error"
    - Add error parameter
    - _Requirements: 1.2_
  
  - [x] 5.5 Write unit tests for audio exceptions
    - Test each audio exception type
    - Verify parameter interpolation
    - _Requirements: 1.1, 1.2_

- [x] 6. Update configuration exception classes
  - [x] 6.1 Update InvalidAPIKeyError (if not done in 4.5)
    - Add translation_key="errors.invalid_api_key"
    - _Requirements: 2.1_
  
  - [x] 6.2 Update MissingConfigError
    - Add translation_key="errors.missing_config"
    - Add parameter parameter
    - _Requirements: 1.2_
  
  - [x] 6.3 Update InvalidConfigError
    - Add translation_key="errors.invalid_config"
    - Add parameter parameter
    - _Requirements: 1.2_
  
  - [x] 6.4 Update HotkeyConflictError
    - Add translation_key="errors.hotkey_conflict"
    - Add hotkey parameter
    - _Requirements: 1.2_
  
  - [x] 6.5 Write unit tests for configuration exceptions
    - Test each config exception type
    - Verify parameter interpolation
    - _Requirements: 1.1, 1.2_

- [x] 7. Checkpoint - Verify all exception classes updated
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Update transcription_client.py error messages
  - [x] 8.1 Update TranscriptionClient.__init__ error handling
    - Replace "API ключ не передан" with InvalidAPIKeyError(provider=provider)
    - Replace "Для custom провайдера требуется base_url и model" with translation key
    - Replace "Неизвестный провайдер" with translation key
    - Replace "Не удалось инициализировать клиент" with translation key
    - _Requirements: 1.1, 1.2_
  
  - [x] 8.2 Update TranscriptionClient.transcribe_audio error handling
    - Replace "Ответ API не содержит поле 'text'" with translation key
    - Update APIAuthenticationError usage
    - Update APINetworkError usage
    - Update APITimeoutError usage
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 8.3 Update TranscriptionClient._prepare_audio_file error handling
    - Replace "Аудио файл не найден" with translation key
    - Replace "Не удалось открыть аудио файл" with translation key
    - _Requirements: 1.2_
  
  - [x] 8.4 Update TranscriptionClient._handle_api_error
    - Replace all Russian error messages with translation keys
    - Update to use new exception classes
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 8.5 Update TranscriptionClient.post_process_text error handling
    - Replace "API ключ для {provider} не передан" with translation key
    - Update all error message strings to use translation keys
    - _Requirements: 1.2, 2.1_
  
  - [x] 8.6 Write integration tests for transcription_client
    - Test error message translation in transcription flow
    - Test parameter interpolation with real provider names
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3_

- [x] 9. Update other service files with Russian error messages
  - [x] 9.1 Update audio_engine.py error messages
    - Replace "Не удалось начать запись" with translation key
    - Replace "Запись не активна" with translation key
    - Replace "Ошибка при остановке записи" with translation key
    - Replace "Не удалось сохранить WAV файл" with translation key
    - _Requirements: 1.2_
  
  - [x] 9.2 Update utils/audio_utils.py error messages
    - Replace "Неподдерживаемая ширина сэмпла" with translation key
    - _Requirements: 1.2_
  
  - [x] 9.3 Update models/data_models.py error messages
    - Replace "Путь к файлу не может быть пустым" with translation key
    - Replace "max_length должен быть положительным числом" with translation key
    - _Requirements: 1.2_
  
  - [x] 9.4 Update main.py error messages
    - Replace "Ошибки в конфигурации" with translation key
    - Replace "Приложение не инициализировано" with translation key
    - _Requirements: 1.1_
  
  - [x] 9.5 Update utils/single_instance.py error messages
    - Replace "{app_name} уже запущен!" with translation key
    - _Requirements: 1.2_
  
  - [x] 9.6 Write unit tests for service file error messages
    - Test error messages from audio_engine
    - Test error messages from audio_utils
    - Test error messages from data_models
    - _Requirements: 1.1, 1.2_

- [x] 10. Update UI notification messages
  - [x] 10.1 Update tray_icon.py notification methods
    - Update show_error_notification to use exception.user_message
    - Update all notification calls to use translation keys
    - Add helper method for translating notification messages
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 10.2 Write property test for notification translation
    - **Property 5: Notification Translation**
    - **Validates: Requirements 3.1, 3.2**
  
  - [x] 10.3 Write unit tests for specific notifications
    - Test success notification translation
    - Test error notification translation
    - Test settings saved notification
    - Test hotkey error notification
    - Test API key missing notification
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 11. Update UI status messages
  - [x] 11.1 Update floating_window.py status display
    - Update status label to use translation keys
    - Add status_key_map for status → translation key mapping
    - Implement update_status method with i18n support
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 11.2 Add language change listener to UI components
    - Implement signal/slot for language changes
    - Update all UI text when language changes
    - _Requirements: 7.4_
  
  - [x] 11.3 Write property test for language switching
    - **Property 11: Language Switching Updates**
    - **Validates: Requirements 7.4**
  
  - [x] 11.4 Write unit tests for status messages
    - Test "Recording..." status translation
    - Test "Processing..." status translation
    - Test "Ready" status translation
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 12. Checkpoint - Verify all UI components updated
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Add fallback and error handling
  - [x] 13.1 Implement English fallback in exception classes
    - Add fallback logic in user_message property
    - Log warning when falling back to English
    - _Requirements: 1.3_
  
  - [x] 13.2 Implement graceful degradation
    - Add try-except around i18n.t() calls
    - Fall back to technical message if i18n fails
    - Log error when i18n system unavailable
    - _Requirements: 8.2_
  
  - [x] 13.3 Implement missing key fallback
    - Update i18n.t() to return key itself if not found
    - Log warning for missing keys
    - _Requirements: 8.4_
  
  - [x] 13.4 Write property test for English fallback
    - **Property 3: English Fallback for Missing Translations**
    - **Validates: Requirements 1.3**
  
  - [x] 13.5 Write property test for graceful degradation
    - **Property 13: Graceful Degradation**
    - **Validates: Requirements 8.2**
  
  - [x] 13.6 Write property test for missing key fallback
    - **Property 14: Missing Key Fallback**
    - **Validates: Requirements 8.4**

- [x] 14. Add logging preservation tests
  - [x] 14.1 Write property test for log message preservation
    - **Property 4: Log Message Preservation**
    - **Validates: Requirements 1.5, 4.1, 4.3, 4.4, 6.5**
  
  - [x] 14.2 Write unit tests for logging behavior
    - Test that logger.info uses technical message
    - Test that logger.error uses technical message
    - Test that log files contain Russian text
    - _Requirements: 1.5, 4.1, 4.3, 4.4_

- [x] 15. Add exception API tests
  - [x] 15.1 Write property test for translation key acceptance
    - **Property 9: Translation Key Acceptance**
    - **Validates: Requirements 6.1**
  
  - [x] 15.2 Write property test for translation key preservation
    - **Property 10: Translation Key Preservation**
    - **Validates: Requirements 6.4**
  
  - [x] 15.3 Write property test for backward compatibility
    - **Property 12: Legacy Exception Support**
    - **Validates: Requirements 8.1, 8.3, 8.5**

- [x] 16. Final checkpoint - Run all tests and verify functionality
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- All user-facing messages must use translation keys
- All log messages must remain in Russian
- Backward compatibility must be maintained throughout
