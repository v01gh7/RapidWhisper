# Implementation Plan: Transcription Formatting

## Overview

This implementation plan breaks down the transcription formatting feature into discrete, incremental coding tasks. The approach focuses on building the core formatting infrastructure first, then integrating with the UI, and finally adding comprehensive testing. Each task builds on previous work to ensure continuous validation.

## Tasks

- [x] 1. Set up formatting module structure and configuration
  - Create `formatting_module.py` with FormattingModule class skeleton
  - Create `formatting_config.py` with FormattingConfig dataclass
  - Add configuration fields to .env: FORMATTING_ENABLED, FORMATTING_PROVIDER, FORMATTING_MODEL, FORMATTING_APPLICATIONS
  - Implement configuration loading from environment variables
  - Implement configuration saving to environment variables
  - _Requirements: 1.7, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 1.1 Write property test for configuration persistence
  - **Property 2: Configuration Round-Trip Persistence**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
  - Test that saving then loading configuration preserves all values

- [x] 1.2 Write property test for configuration independence
  - **Property 1: Configuration Independence**
  - **Validates: Requirements 1.7, 4.5, 7.6**
  - Test that formatting config changes don't affect transcription/post-processing configs

- [x] 2. Implement format mapping and detection logic
  - Create FORMAT_MAPPINGS dictionary with application patterns (Notion, Obsidian, Word, Markdown, etc.)
  - Implement `match_application_to_format()` function for matching app names and file extensions
  - Implement `FormattingModule.get_active_application_format()` to detect and match active window
  - Integrate with existing `window_monitor.py` for active window detection
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 2.1 Write property test for window detection completeness
  - **Property 3: Window Detection Completeness**
  - **Validates: Requirements 3.1, 3.2, 3.3**
  - Test that window detection returns complete information

- [x] 2.2 Write property test for application format matching
  - **Property 4: Application Format Matching**
  - **Validates: Requirements 3.4, 3.5**
  - Test that matching logic is deterministic for same inputs

- [x] 2.3 Write unit tests for specific format detection
  - Test Notion application detection
  - Test Obsidian application detection
  - Test .md file extension detection
  - Test Word application detection
  - Test no-match scenario
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 3. Implement format-specific prompts
  - Create FORMAT_PROMPTS dictionary with prompts for each format type (Notion, Obsidian, Markdown, Word)
  - Implement `get_format_prompt()` function to retrieve format-specific prompts
  - Implement `FormattingModule.get_format_prompt()` method
  - _Requirements: 4.2, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.1 Write property test for format-specific prompt selection
  - **Property 6: Format-Specific Prompt Selection**
  - **Validates: Requirements 4.2, 6.5**
  - Test that each format type gets appropriate prompt

- [x] 3.2 Write unit tests for prompt content
  - Test Notion prompt contains Notion-specific instructions
  - Test Obsidian prompt contains wiki-link instructions
  - Test Markdown prompt contains standard markdown syntax
  - Test Word prompt avoids markdown syntax
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 4. Implement AI client integration for formatting
  - Implement `FormattingModule.format_text()` to send text to AI provider
  - Create separate AI client instance for formatting (reuse existing infrastructure)
  - Implement provider selection logic (groq, openai, glm, custom)
  - Implement model selection from configuration
  - Add error handling: return original text on failure, log errors
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 4.1 Write property test for provider configuration selection
  - **Property 11: Provider Configuration Selection**
  - **Validates: Requirements 7.2, 7.3**
  - Test that formatting uses its own provider/model config

- [x] 4.2 Write property test for graceful failure handling
  - **Property 12: Graceful Failure Handling**
  - **Validates: Requirements 7.4, 7.5**
  - Test that AI failures return original text and log errors

- [x] 5. Implement formatting-only processing path
  - Implement `FormattingModule.should_format()` to check if formatting is enabled
  - Implement `FormattingModule.process()` as main entry point
  - Implement logic: if formatting enabled AND format matches, format text; otherwise return original
  - _Requirements: 4.1, 4.3, 4.4, 4.5_

- [x] 5.1 Write property test for formatting decision logic
  - **Property 5: Formatting Decision Logic**
  - **Validates: Requirements 4.1, 4.4, 5.1, 5.6**
  - Test correct processing decision for all state combinations

- [x] 5.2 Write property test for original text preservation
  - **Property 7: Original Text Preservation on No-Match**
  - **Validates: Requirements 4.4**
  - Test that non-matching applications preserve original text

- [x] 6. Checkpoint - Test formatting module in isolation
  - Ensure all formatting module tests pass
  - Manually test format detection with different applications
  - Verify error handling works correctly
  - Ask the user if questions arise

- [x] 7. Implement processing coordinator for combined operations
  - Create `processing_coordinator.py` with ProcessingCoordinator class
  - Implement `should_combine_operations()` to determine if both formatting and post-processing are enabled
  - Implement `combine_prompts()` to merge post-processing and formatting prompts
  - Implement `process_transcription()` as main orchestration method
  - Add logic to route to: formatting-only, combined, post-processing-only, or no processing
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 7.1 Write property test for single API call in combined mode
  - **Property 8: Single API Call for Combined Operations**
  - **Validates: Requirements 5.1, 5.4**
  - Test that combined operations make exactly one API request

- [x] 7.2 Write property test for combined prompt composition
  - **Property 9: Combined Prompt Composition**
  - **Validates: Requirements 5.3**
  - Test that combined prompt contains both sets of instructions

- [x] 7.3 Write property test for post-processing provider priority
  - **Property 10: Post-Processing Provider Priority**
  - **Validates: Requirements 5.2, 5.7**
  - Test that combined operations use post-processing provider

- [x] 7.4 Write integration tests for processing coordinator
  - Test formatting-only pipeline
  - Test combined formatting + post-processing pipeline
  - Test post-processing-only pipeline (no format match)
  - Test disabled state (no processing)
  - _Requirements: 4.1, 5.1, 5.6_

- [x] 8. Integrate formatting into transcription pipeline
  - Modify existing transcription pipeline to instantiate ProcessingCoordinator
  - Add call to `process_transcription()` after transcription completes
  - Ensure formatting happens before final output is returned
  - Test end-to-end flow: transcription → formatting → output
  - _Requirements: 4.1, 4.3, 5.1_

- [x] 9. Checkpoint - Test integrated pipeline
  - Ensure all integration tests pass
  - Test complete transcription flow with formatting enabled
  - Test complete transcription flow with both formatting and post-processing enabled
  - Verify no regressions in existing transcription functionality
  - Ask the user if questions arise

- [x] 10. Implement formatting settings UI
  - Create `FormattingSettingsWidget` class in `processing_page.py` (or new file)
  - Add QGroupBox with title "Formatting (Форматирование)"
  - Add enable/disable checkbox
  - Add AI provider dropdown (groq, openai, glm, custom)
  - Add model input field (QLineEdit)
  - Add applications list input field (QLineEdit with placeholder for comma-separated values)
  - Add informational label explaining the feature
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 8.1, 8.2, 8.4, 8.5_

- [x] 10.1 Write unit tests for UI components
  - Test that FormattingSettingsWidget creates all required controls
  - Test that enable/disable checkbox exists
  - Test that provider dropdown contains correct options
  - Test that model field exists
  - Test that applications field exists with correct placeholder
  - Test that info label exists
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 11. Implement UI settings persistence
  - Implement `FormattingSettingsWidget.load_settings()` to load from FormattingConfig
  - Implement `FormattingSettingsWidget.save_settings()` to save to FormattingConfig
  - Connect UI changes to configuration updates
  - Add validation for required fields (provider, model, applications)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 11.1 Write unit tests for UI settings persistence
  - Test that settings load correctly into UI
  - Test that UI saves settings correctly
  - Test that validation works for empty fields
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 12. Integrate formatting settings into Processing settings page
  - Add FormattingSettingsWidget to existing Processing settings page
  - Position below or near post-processing settings
  - Ensure consistent styling with other settings sections
  - Test that settings page layout looks correct
  - _Requirements: 1.1, 8.1, 8.2_

- [x] 13. Add localization support
  - Add Russian translations for all UI labels
  - "Formatting" / "Форматирование"
  - "Enable formatting" / "Включить форматирование"
  - "AI Provider" / "AI провайдер"
  - "Model" / "Модель"
  - "Applications" / "Приложения"
  - Add bilingual info text explaining the feature
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 14. Final checkpoint - End-to-end testing
  - Test complete flow: configure settings → transcribe → verify formatting applied
  - Test with different applications (Notion, Obsidian, Word, Markdown)
  - Test combined formatting + post-processing
  - Test error scenarios (invalid config, AI failure)
  - Verify all property tests pass (100+ iterations each)
  - Verify all unit tests pass
  - Ask the user if questions arise

- [x] 15. Documentation and cleanup
  - Add code comments explaining key logic
  - Document configuration options in README or user guide
  - Add examples of supported applications
  - Clean up any debug logging or temporary code
  - _Requirements: All_

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: core logic → integration → UI → testing
