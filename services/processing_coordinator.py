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
        # CRITICAL: Both steps are MANDATORY and MUST be applied
        # Step 1: Fix grammar and punctuation
        # Step 2: Apply formatting to the corrected text (THIS IS REQUIRED!)
        combined = f"""CRITICAL: You MUST complete BOTH steps below. Do not skip step 2!

STEP 1 - Grammar and Punctuation Correction:
{post_prompt}

STEP 2 - Formatting (MANDATORY - DO NOT SKIP THIS STEP):
After correcting grammar and punctuation in step 1, you MUST apply the following formatting rules to the corrected text:

{format_prompt}

IMPORTANT: Both steps are required. Output must be both corrected AND formatted."""
        
        logger.debug(f"Combined prompt length: {len(combined)} characters")
        return combined
    
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
        
        # Check if only formatting is enabled
        if self.formatting_module.should_format():
            format_type = self.formatting_module.get_active_application_format()
            if format_type:
                logger.info("FORMATTING ONLY MODE: Applying formatting")
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
            # Get format prompt (either app-specific or fallback)
            if format_type == "fallback":
                format_prompt = self.formatting_module.config.get_prompt_for_app("_fallback")
                logger.info("Using fallback formatting prompt for unknown application")
            else:
                format_prompt = self.formatting_module.get_format_prompt(format_type)
                logger.info(f"Using app-specific formatting prompt for: {format_type}")
            
            # Combine prompts
            combined_prompt = self.combine_prompts(
                config.post_processing_prompt,
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
            elif config.post_processing_provider == "llm":
                api_key = config.llm_api_key
            
            processed_text = transcription_client.post_process_text(
                text=text,
                provider=config.post_processing_provider,
                model=model_to_use,
                system_prompt=combined_prompt,
                api_key=api_key,
                base_url=config.llm_base_url if config.post_processing_provider == "llm" else None,
                use_coding_plan=config.glm_use_coding_plan if config.post_processing_provider == "glm" else False
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
            elif config.post_processing_provider == "llm":
                api_key = config.llm_api_key
            
            processed_text = transcription_client.post_process_text(
                text=text,
                provider=config.post_processing_provider,
                model=model_to_use,
                system_prompt=config.post_processing_prompt,
                api_key=api_key,
                base_url=config.llm_base_url if config.post_processing_provider == "llm" else None,
                use_coding_plan=config.glm_use_coding_plan if config.post_processing_provider == "glm" else False
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
            elif provider == "custom":
                api_key = formatting_config.custom_api_key
            
            # Make API call with fallback prompt
            formatted_text = transcription_client.post_process_text(
                text=text,
                provider=provider,
                model=model,
                system_prompt=fallback_prompt,
                api_key=api_key,
                temperature=temperature
            )
            
            # Check if formatting actually worked
            if formatted_text != text:
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
