"""
Processing Coordinator for Transcription Formatting Feature.

This module coordinates formatting and post-processing operations,
deciding between formatting-only, combined, or post-processing-only modes
to minimize API calls and optimize processing.
"""

from typing import Optional, Tuple
from services.formatting_module import FormattingModule
from services.formatting_config import FormattingConfig
from utils.logger import get_logger
from utils.text_guard import has_extra_tokens

logger = get_logger()


class ProcessingCoordinator:
    """
    Coordinates formatting and post-processing operations.
    
    This coordinator orchestrates the processing pipeline, deciding whether to:
    - Apply formatting only (when post-processing is disabled)
    - Apply post-processing only (when formatting is disabled or no format match)
    - Combine both operations in a single AI call (when both are enabled and format matches)
    - Return original text (when both are disabled)
    """
    
    def __init__(self, formatting_module: FormattingModule, config_manager):
        """
        Initialize the coordinator.
        
        Args:
            formatting_module: Formatting module instance
            config_manager: Configuration manager for loading settings
        """
        self.formatting_module = formatting_module
        self.config_manager = config_manager
        logger.info("ProcessingCoordinator initialized")
    
    def should_combine_operations(self) -> Tuple[bool, Optional[str]]:
        """
        Determine if operations should be combined.
        
        Returns:
            Tuple[bool, Optional[str]]: (should_combine, format_type_or_fallback)
                - should_combine: True if both formatting and post-processing are enabled
                - format_type_or_fallback: The matched format type, or "fallback" if no match
        """
        # Check if formatting is enabled
        if not self.formatting_module.should_format():
            logger.debug("Formatting disabled, cannot combine operations")
            return False, None
        
        # Check if post-processing is enabled
        config = self.config_manager
        if not config.enable_post_processing:
            logger.debug("Post-processing disabled, cannot combine operations")
            return False, None

        if not getattr(config, "combine_post_processing_with_formatting", True):
            logger.info("Combined mode disabled in config")
            return False, None
        
        # Check if active application matches a format
        format_type = self.formatting_module.get_active_application_format()
        if format_type is None:
            logger.info("Both formatting and post-processing enabled, but no format match - using fallback")
            return True, "fallback"
        
        logger.info(f"Both formatting and post-processing enabled with format match: {format_type}")
        return True, format_type
    
    def combine_prompts(self, post_prompt: str, format_prompt: str) -> str:
        """
        Combine post-processing and formatting prompts into single prompt.
        
        CRITICAL ORDER: Post-processing FIRST, then formatting.
        1. First fix grammar, punctuation, and sentence structure
        2. Then apply formatting based on corrected text
        
        This order is important because formatting depends on correct punctuation
        to identify sentence boundaries, lists, and paragraph breaks.
        
        Args:
            post_prompt: Post-processing system prompt (grammar/punctuation fixes)
            format_prompt: Formatting system prompt (structure/styling)
        
        Returns:
            str: Combined system prompt with correct order
        """
        # CRITICAL: Both steps are MANDATORY and MUST be applied.
        # The model must output ONLY the final corrected + formatted text.
        combined = f"""CRITICAL: Do BOTH actions internally, in this order: fix grammar/punctuation, then apply formatting.
Output ONLY the final corrected + formatted text.
NEVER output steps, outlines, explanations, examples, or code blocks.
Do NOT add new facts, examples, or content that isn't in the input.
You MAY replace words to fix errors, remove repetition, and improve clarity WITHOUT adding new meaning.

Grammar & punctuation rules:
{post_prompt}

Formatting rules (apply AFTER grammar fixes):
{format_prompt}

OUTPUT RULES (HIGHEST PRIORITY):
- Output EXACTLY ONE final version (no intermediate text).
- No separators, no "Step" labels, no headings like "Step 1".
- If any rules conflict, follow these output rules."""
        
        logger.debug(f"Combined prompt length: {len(combined)} characters")
        return combined

    def _build_post_processing_prompt(self, base_prompt: str) -> str:
        """
        Build a post-processing prompt that allows replacements but forbids new content.
        """
        return (
            "CRITICAL OVERRIDE:\n"
            "- You MAY replace words to fix errors, remove repetition, and improve clarity.\n"
            "- You MUST NOT add new facts, examples, code, or instructions.\n"
            "- If any rule conflicts with this override, follow the override.\n\n"
            f"{base_prompt}"
        )

    def _run_hook_event(self, event: str, text: str, format_type: Optional[str] = None, combined: bool = False) -> str:
        try:
            from services.hooks_manager import get_hook_manager, build_hook_options
            options = build_hook_options(
                event,
                data={
                    "text": text,
                    "format_type": format_type,
                    "combined": combined
                }
            )
            options = get_hook_manager().run_event(event, options)
            return options.get("data", {}).get("text", text)
        except Exception as e:
            logger.error(f"Hook {event} failed: {e}")
            return text
    
    def process_transcription(
        self,
        text: str,
        transcription_client,
        config
    ) -> str:
        """
        Process transcribed text through formatting and/or post-processing.
        
        Decision logic:
        - If only formatting enabled: use formatting module
        - If only post-processing enabled: use post-processing module
        - If both enabled and format matches: combine operations in single AI call
        - If neither enabled: return original text
        
        Args:
            text: Original transcribed text
            transcription_client: Client for making AI requests
            config: Configuration object with post-processing settings
        
        Returns:
            str: Processed text
        """
        logger.info("=" * 80)
        logger.info("PROCESSING COORDINATOR: Starting text processing")
        logger.info(f"Text length: {len(text)} characters")
        
        # Check if we should combine operations
        should_combine, format_type = self.should_combine_operations()
        
        if should_combine:
            logger.info("COMBINED MODE: Formatting + Post-processing in single API call")
            return self._process_combined(text, format_type, transcription_client, config)

        if (
            self.formatting_module.should_format()
            and config.enable_post_processing
            and not getattr(config, "combine_post_processing_with_formatting", True)
        ):
            logger.info("SEQUENTIAL MODE: Post-processing then formatting")
            # Step 1: post-processing
            text = self._process_post_processing_only(text, transcription_client, config)

            # Step 2: formatting
            format_type = self.formatting_module.get_active_application_format()
            if format_type:
                logger.info("FORMATTING STEP: Applying formatting after post-processing")
                text = self._run_hook_event("formatting_step", text, format_type=format_type)
                return self.formatting_module.format_text(text, format_type)

            logger.info("No format match after post-processing - applying fallback formatting")
            return self._process_fallback_formatting(text, transcription_client, config)
        
        # Check if only formatting is enabled
        if self.formatting_module.should_format():
            format_type = self.formatting_module.get_active_application_format()
            if format_type:
                logger.info("FORMATTING ONLY MODE: Applying formatting")
                text = self._run_hook_event("formatting_step", text, format_type=format_type)
                return self.formatting_module.process(text)
            else:
                logger.info("No format match - applying fallback formatting")
                # Apply fallback formatting for unknown applications
                return self._process_fallback_formatting(text, transcription_client, config)
        
        # Check if post-processing is enabled (either alone or when formatting had no match)
        if config.enable_post_processing:
            logger.info("POST-PROCESSING ONLY MODE: Applying post-processing")
            return self._process_post_processing_only(text, transcription_client, config)
        
        # Neither enabled
        logger.info("NO PROCESSING: Both formatting and post-processing disabled")
        return text
    
    def _process_combined(
        self,
        text: str,
        format_type: str,
        transcription_client,
        config
    ) -> str:
        """
        Process text with combined formatting and post-processing.
        
        Uses the post-processing AI provider with a combined prompt.
        
        Args:
            text: Original text
            format_type: Format identifier or "fallback" for unknown applications
            transcription_client: Client for making AI requests
            config: Configuration object
        
        Returns:
            str: Processed text
        """
        try:
            text = self._run_hook_event("formatting_step", text, format_type=format_type, combined=True)
            text = self._run_hook_event("post_formatting_step", text, format_type=format_type, combined=True)
            # Get format prompt (either app-specific or fallback)
            if format_type == "fallback":
                format_prompt = self.formatting_module.config.get_prompt_for_app("_fallback")
                logger.info("Using fallback formatting prompt for unknown application")
            else:
                format_prompt = self.formatting_module.get_format_prompt(format_type)
                logger.info(f"Using app-specific formatting prompt for: {format_type}")
            
            # Combine prompts
            combined_prompt = self.combine_prompts(
                self._build_post_processing_prompt(config.post_processing_prompt),
                format_prompt
            )
            
            logger.info(f"Combined prompt created (length: {len(combined_prompt)})")
            logger.info(f"Using post-processing provider: {config.post_processing_provider}")
            
            # Determine which model to use
            model_to_use = (
                config.post_processing_custom_model 
                if config.post_processing_custom_model 
                else config.post_processing_model
            )
            
            logger.info(f"Using model: {model_to_use}")
            
            # Make single API call with combined prompt
            # Get API key for post-processing provider
            from core.config_loader import get_config_loader
            config_loader = get_config_loader()
            
            api_key = None
            if config.post_processing_provider == "groq":
                api_key = config_loader.get("ai_provider.api_keys.groq")
            elif config.post_processing_provider == "openai":
                api_key = config_loader.get("ai_provider.api_keys.openai")
            elif config.post_processing_provider == "glm":
                api_key = config_loader.get("ai_provider.api_keys.glm")
            elif config.post_processing_provider == "zai":
                # Z.AI использует GLM_API_KEY
                api_key = config_loader.get("ai_provider.api_keys.glm")
            elif config.post_processing_provider == "llm":
                api_key = config.llm_api_key
            
            processed_text = transcription_client.post_process_text(
                text=text,
                provider=config.post_processing_provider,
                model=model_to_use,
                system_prompt=combined_prompt,
                api_key=api_key,
                base_url=config.llm_base_url if config.post_processing_provider == "llm" else None,
                use_coding_plan=config.glm_use_coding_plan if config.post_processing_provider == "glm" else False,
                max_tokens=config.post_processing_max_tokens
            )
            
            # Check if processing actually worked (not just returned original text)
            if processed_text != text:
                logger.info("✅ Combined processing completed successfully")
                logger.info(f"Result preview: {processed_text[:100]}...")
                return processed_text
            else:
                logger.warning("⚠️ API returned original text (likely due to error)")
                logger.info("Returning original text without formatting")
                return text
            
        except Exception as e:
            logger.error(f"❌ Combined processing failed: {e}")
            logger.warning("⚠️ Returning original text without formatting")
            # Пробросить исключение для уведомления пользователя
            raise
    
    def _process_post_processing_only(
        self,
        text: str,
        transcription_client,
        config
    ) -> str:
        """
        Process text with post-processing only.
        
        Args:
            text: Original text
            transcription_client: Client for making AI requests
            config: Configuration object
        
        Returns:
            str: Processed text
        """
        try:
            text = self._run_hook_event("post_formatting_step", text)
            # Determine which model to use
            model_to_use = (
                config.post_processing_custom_model 
                if config.post_processing_custom_model 
                else config.post_processing_model
            )
            
            logger.info(f"Using provider: {config.post_processing_provider}")
            logger.info(f"Using model: {model_to_use}")
            
            # Get API key for post-processing provider
            from core.config_loader import get_config_loader
            config_loader = get_config_loader()
            
            api_key = None
            if config.post_processing_provider == "groq":
                api_key = config_loader.get("ai_provider.api_keys.groq")
            elif config.post_processing_provider == "openai":
                api_key = config_loader.get("ai_provider.api_keys.openai")
            elif config.post_processing_provider == "glm":
                api_key = config_loader.get("ai_provider.api_keys.glm")
            elif config.post_processing_provider == "zai":
                # Z.AI использует GLM_API_KEY
                api_key = config_loader.get("ai_provider.api_keys.glm")
            elif config.post_processing_provider == "llm":
                api_key = config.llm_api_key
            
            processed_text = transcription_client.post_process_text(
                text=text,
                provider=config.post_processing_provider,
                model=model_to_use,
                system_prompt=self._build_post_processing_prompt(config.post_processing_prompt),
                api_key=api_key,
                base_url=config.llm_base_url if config.post_processing_provider == "llm" else None,
                use_coding_plan=config.glm_use_coding_plan if config.post_processing_provider == "glm" else False,
                max_tokens=config.post_processing_max_tokens
            )
            
            # Check if processing actually worked
            if processed_text != text:
                logger.info("✅ Post-processing completed successfully")
                return processed_text
            else:
                logger.warning("⚠️ API returned original text (likely due to error)")
                logger.info("Returning original text without post-processing")
                return text
            
        except Exception as e:
            logger.error(f"❌ Post-processing failed: {e}")
            logger.warning("⚠️ Returning original text without post-processing")
            # Пробросить исключение для уведомления пользователя
            raise

    def _process_fallback_formatting(
        self,
        text: str,
        transcription_client,
        config
    ) -> str:
        """
        Process text with fallback formatting for unknown applications.
        
        This applies basic formatting (sentence breaks, paragraphs, headings)
        when the active application doesn't match any configured format.
        Uses the editable _fallback prompt from configuration.
        
        Args:
            text: Original text
            transcription_client: Client for making AI requests
            config: Configuration object
        
        Returns:
            str: Formatted text
        """
        try:
            text = self._run_hook_event("formatting_step", text, format_type="fallback")
            logger.info("FALLBACK FORMATTING MODE: Applying universal formatting")
            
            # Get fallback prompt from configuration (editable by user)
            fallback_prompt = self.formatting_module.config.get_prompt_for_app("_fallback")
            
            # Use formatting provider and model
            formatting_config = self.formatting_module.config
            provider = formatting_config.provider
            model = formatting_config.get_model()
            temperature = formatting_config.temperature
            
            logger.info(f"Using formatting provider: {provider}")
            logger.info(f"Using model: {model}")
            logger.info(f"Temperature: {temperature}")
            logger.info(f"Fallback prompt length: {len(fallback_prompt)} characters")
            
            # Get API key for formatting provider
            from core.config_loader import get_config_loader
            config_loader = get_config_loader()
            
            api_key = None
            if provider == "groq":
                api_key = config_loader.get("ai_provider.api_keys.groq")
            elif provider == "openai":
                api_key = config_loader.get("ai_provider.api_keys.openai")
            elif provider == "glm":
                api_key = config_loader.get("ai_provider.api_keys.glm")
            elif provider == "zai":
                # Z.AI использует GLM_API_KEY
                api_key = config_loader.get("ai_provider.api_keys.glm")
            elif provider == "custom":
                api_key = formatting_config.custom_api_key
            
            # Make API call with fallback prompt
            formatted_text = transcription_client.post_process_text(
                text=text,
                provider=provider,
                model=model,
                system_prompt=fallback_prompt,
                api_key=api_key,
                temperature=temperature,
                max_tokens=config.post_processing_max_tokens
            )
            
            # Check if formatting actually worked
            if formatted_text != text:
                if formatted_text and has_extra_tokens(text, formatted_text):
                    logger.warning("⚠️ Fallback formatting added new words - returning original text")
                    return text
                logger.info("✅ Fallback formatting completed successfully")
                logger.info(f"Result preview: {formatted_text[:100]}...")
                return formatted_text
            else:
                logger.warning("⚠️ API returned original text (likely due to error)")
                logger.info("Returning original text without formatting")
                return text
            
        except Exception as e:
            logger.error(f"❌ Fallback formatting failed: {e}")
            logger.warning("⚠️ Returning original text without formatting")
            # Пробросить исключение для уведомления пользователя
            raise
