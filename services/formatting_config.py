"""
Configuration module for transcription formatting feature.

This module provides the FormattingConfig dataclass for managing
formatting settings including AI provider, model, and target applications.
"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
# DEPRECATED: dotenv imports kept for backward compatibility with tests only
from dotenv import load_dotenv, set_key
from core.prompt_defaults import get_default_transcript_prompt
from utils.logger import get_logger

logger = get_logger()


# Canonical fallback prompt comes from config/prompts/_fallback.txt.
FALLBACK_FORMATTING_PROMPT = get_default_transcript_prompt()

# Backward compatibility alias for tests
UNIVERSAL_DEFAULT_PROMPT = FALLBACK_FORMATTING_PROMPT


def migrate_from_old_format(applications_str: str) -> Dict[str, Dict[str, Any]]:
    """
    Migrate from old comma-separated format to new JSON format.
    
    Args:
        applications_str: Comma-separated application names
        
    Returns:
        Dictionary in new format with empty prompts
    """
    apps = [app.strip() for app in applications_str.split(",") if app.strip()]
    return {
        app: {"enabled": True, "prompt": ""}
        for app in apps
    }


@dataclass
class FormattingConfig:
    """
    Formatting configuration data model.
    
    Attributes:
        enabled: Whether formatting is enabled
        provider: AI provider for formatting (groq, openai, glm, custom)
        model: Model name for formatting
        applications: List of application names to format for (kept for backward compatibility)
        temperature: Temperature for AI model (0.0-1.0, lower = more deterministic)
        system_prompt: System prompt for formatting (deprecated, kept for migration)
        app_prompts: Dictionary mapping application names to their custom prompts
        custom_base_url: Base URL for custom provider (e.g., http://localhost:1234/v1/)
        custom_api_key: API key for custom provider
        web_app_keywords: Dictionary mapping format types to lists of keywords for browser detection
    """
    
    enabled: bool = False
    provider: str = "groq"  # groq, openai, glm, custom
    model: str = ""
    applications: List[str] = field(default_factory=list)
    temperature: float = 0.3  # Lower temperature for more consistent formatting
    system_prompt: str = ""  # Deprecated, kept for migration
    app_prompts: Dict[str, str] = field(default_factory=dict)  # New: per-application prompts
    custom_base_url: str = ""  # For custom provider
    custom_api_key: str = ""  # For custom provider
    web_app_keywords: Dict[str, List[str]] = field(default_factory=dict)  # Keywords for browser detection
    use_fixed_format: bool = False  # If True, always use fallback prompt regardless of active application
    
    def is_valid(self) -> bool:
        """
        Validate configuration completeness.
        
        Returns:
            bool: True if configuration is valid and complete
        """
        # Model is optional - if not specified, default model for provider will be used
        return (
            self.provider in ["groq", "openai", "glm", "custom"] and
            bool(self.applications) and
            0.0 <= self.temperature <= 1.0
        )
    
    def get_model(self) -> str:
        """
        Get model name, using default for provider if not specified.
        
        Returns:
            str: Model name to use
        """
        if self.model:
            return self.model
        
        # Default models for each provider
        default_models = {
            "groq": "llama-3.3-70b-versatile",
            "openai": "gpt-4o-mini",
            "glm": "glm-4-flash",
            "custom": ""
        }
        
        return default_models.get(self.provider, "")
    
    def get_prompt_for_app(self, app_name: str) -> str:
        """
        Get the prompt for a specific application.
        
        Args:
            app_name: Application name or "_fallback" for unknown apps
            
        Returns:
            Application-specific prompt from .env, or FALLBACK_FORMATTING_PROMPT if not set
        """
        # All prompts come from .env file (self.app_prompts)
        # No hardcoded defaults!
        
        # Special handling for _fallback
        if app_name == "_fallback":
            prompt = self.app_prompts.get("_fallback", "")
        # For known applications
        elif app_name in self.applications:
            prompt = self.app_prompts.get(app_name, "")
        # For unknown applications
        else:
            prompt = self.app_prompts.get("_fallback", "")
        
        # Decode \\n to actual newlines for display/use
        # JSON stores them as \\n, we need real newlines
        if prompt:
            return prompt.replace('\\n', '\n')
        else:
            # If no prompt found, return fallback
            return FALLBACK_FORMATTING_PROMPT
    
    def get_format_type(self, app_name: str) -> str:
        """
        Get the format type for an application (markdown or html).
        
        Args:
            app_name: Application name
            
        Returns:
            "html" for Word/LibreOffice/Google Docs, "markdown" for others
        """
        # Word/LibreOffice/Google Docs use HTML
        if app_name in ["word", "libreoffice"]:
            return "html"
        # Everything else uses markdown
        else:
            return "markdown"
    
    def set_prompt_for_app(self, app_name: str, prompt: str) -> None:
        """
        Set the prompt for a specific application.
        
        Args:
            app_name: Application name
            prompt: Prompt text (empty string to use default)
        """
        # Encode actual newlines to \\n for storage in JSON
        # This way they survive the .env file format
        self.app_prompts[app_name] = prompt.replace('\n', '\\n') if prompt else ""
    
    @classmethod
    def from_env(cls, env_path: Optional[str] = None) -> 'FormattingConfig':
        """
        Load formatting configuration from config.jsonc.
        
        DEPRECATED: This method name is kept for backward compatibility.
        It now loads from config.jsonc, not .env files.
        
        Args:
            env_path: DEPRECATED - ignored, kept for backward compatibility with tests
        
        Returns:
            FormattingConfig: Configuration loaded from config.jsonc
        """
        # Always load from config.jsonc (new format)
        from core.config_loader import get_config_loader
        config_loader = get_config_loader()
        return cls.from_config(config_loader)
    
    @classmethod
    def from_config(cls, config_loader) -> 'FormattingConfig':
        """
        Load formatting configuration from config.jsonc.
        
        Args:
            config_loader: ConfigLoader instance
        
        Returns:
            FormattingConfig: Configuration loaded from config.jsonc
        """
        config_loader.load()
        
        # Get formatting section
        enabled = config_loader.get("formatting.enabled", False)
        provider = config_loader.get("formatting.provider", "groq")
        model = config_loader.get("formatting.model", "")
        temperature = config_loader.get("formatting.temperature", 0.3)
        
        # Get custom provider settings
        custom_base_url = config_loader.get("formatting.custom.base_url", "")
        # API key is stored in secrets.json and merged into config by ConfigLoader
        custom_api_key = config_loader.get("formatting.custom.api_key", "")
        
        # Get web app keywords
        web_app_keywords = config_loader.get("formatting.web_app_keywords", {})
        
        # Get use_fixed_format setting
        use_fixed_format = config_loader.get("formatting.use_fixed_format", False)
        
        # Get application list from app_prompts keys
        app_prompts_paths = config_loader.get("formatting.app_prompts", {})
        applications = list(app_prompts_paths.keys())
        
        # Load prompts from files
        app_prompts = {}
        for app_name in applications:
            prompt = config_loader.get_prompt(app_name)
            # Encode newlines for storage (to match .env format)
            app_prompts[app_name] = prompt.replace('\n', '\\n') if prompt else ""
        
        logger.info(f"Loaded formatting config from config.jsonc: {len(applications)} applications")
        
        return cls(
            enabled=enabled,
            provider=provider,
            model=model,
            applications=applications,
            temperature=temperature,
            system_prompt="",  # Deprecated
            app_prompts=app_prompts,
            custom_base_url=custom_base_url,
            custom_api_key=custom_api_key,
            web_app_keywords=web_app_keywords,
            use_fixed_format=use_fixed_format
        )
    
    def save_to_config(self, preserve_web_keywords_if_empty: bool = True) -> None:
        """
        Save configuration to config.jsonc and secrets.json.
        
        This is the NEW method that saves to JSONC format.
        """
        from core.config_saver import get_config_saver
        from core.config_loader import get_config_loader
        
        try:
            # Load current config
            config_loader = get_config_loader()
            config_loader.load()
            config = config_loader.config
            
            # Update formatting section
            if "formatting" not in config:
                config["formatting"] = {}
            
            config["formatting"]["enabled"] = self.enabled
            config["formatting"]["provider"] = self.provider
            config["formatting"]["model"] = self.model
            config["formatting"]["temperature"] = self.temperature
            
            # Update custom provider settings (base_url in config, API key in secrets)
            if "custom" not in config["formatting"]:
                config["formatting"]["custom"] = {}
            config["formatting"]["custom"]["base_url"] = self.custom_base_url
            # Note: api_key is NOT saved here - it goes to secrets.json below
            
            # Update web app keywords
            existing_keywords = config.get("formatting", {}).get("web_app_keywords", {})
            if preserve_web_keywords_if_empty and not self.web_app_keywords and existing_keywords:
                config["formatting"]["web_app_keywords"] = existing_keywords
            else:
                config["formatting"]["web_app_keywords"] = self.web_app_keywords
            
            # Update use_fixed_format setting
            config["formatting"]["use_fixed_format"] = self.use_fixed_format
            
            # Update app_prompts paths (keep existing structure)
            if "app_prompts" not in config["formatting"]:
                config["formatting"]["app_prompts"] = {}
            
            # Ensure all applications have prompt file paths
            for app_name in self.applications:
                if app_name not in config["formatting"]["app_prompts"]:
                    config["formatting"]["app_prompts"][app_name] = f"config/prompts/{app_name}.txt"
            
            # Save config
            config_saver = get_config_saver()
            config_saver.save_config(config)
            
            # Save prompts to files
            for app_name in self.applications:
                prompt = self.app_prompts.get(app_name, "")
                # Decode \\n to actual newlines for file storage
                prompt = prompt.replace('\\n', '\n')
                config_saver.save_prompt(app_name, prompt)
            
            # Save API key to secrets.json
            if self.custom_api_key:
                config_saver.update_secret("formatting.custom.api_key", self.custom_api_key)
            
            logger.info("✓ Saved formatting configuration to config.jsonc")
            
        except Exception as e:
            logger.error(f"Failed to save formatting configuration: {e}")
            raise
    
    def save_to_env(self, env_path: Optional[str] = None) -> None:
        """
        Save configuration to config.jsonc and secrets.json.
        
        DEPRECATED: This method name is kept for backward compatibility.
        It now saves to config.jsonc, not .env files.
        
        Args:
            env_path: DEPRECATED - ignored, kept for backward compatibility with tests
        """
        # Always save to config.jsonc (new format)
        self.save_to_config()
