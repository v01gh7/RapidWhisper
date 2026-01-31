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
from dotenv import load_dotenv, set_key
from utils.logger import get_logger

logger = get_logger()


# Universal default prompt that works for all application formats
UNIVERSAL_DEFAULT_PROMPT = """CRITICAL: You are a TEXT FORMATTER, not a writer. Your ONLY job is to format existing text.

STRICT RULES:
1. DO NOT ADD ANY NEW WORDS - Use ONLY the words from the original text
2. DO NOT EXPLAIN - No descriptions, no examples, no elaborations
3. DO NOT EXPAND - Keep the exact same content, just reorganize it
4. DO NOT COMPLETE - If a sentence is incomplete, leave it incomplete

ALLOWED ACTIONS:
- ANALYZE the content and identify natural sections
- CREATE headings where appropriate for main topics and subtopics
- CONVERT lists when the speaker mentions multiple items
- ADD emphasis for important points
- INSERT line breaks between logical sections
- STRUCTURE the content for maximum readability

FORBIDDEN ACTIONS:
- Adding explanations (like "This is used for...")
- Adding descriptions (like "These items are...")
- Adding context or background information
- Completing incomplete thoughts
- Adding examples that weren't spoken

Task: Transform the transcribed speech into well-structured text using ONLY the original words.

Remember: Use ALL the original words, just organize them better. Zero tolerance for additions.

Output ONLY the reformatted text."""


# Fallback formatting prompt for unknown applications
# Simple, universal formatting that makes text readable
FALLBACK_FORMATTING_PROMPT = """CRITICAL: You are a TEXT FORMATTER, not a writer. Your ONLY job is to format existing text.

STRICT RULES:
1. DO NOT ADD ANY NEW WORDS - Use ONLY the words from the original text
2. DO NOT EXPLAIN - No descriptions, no examples, no elaborations
3. DO NOT EXPAND - If the text says "orange sticks for manicure", output ONLY "orange sticks for manicure"
4. DO NOT COMPLETE - If a sentence is incomplete, leave it incomplete

ALLOWED ACTIONS:
- Add line breaks between sentences
- Group sentences into paragraphs
- Add basic punctuation if missing

FORBIDDEN ACTIONS:
- Adding explanations (like "They are used for...")
- Adding descriptions (like "These sticks are...")
- Adding context or background information
- Completing incomplete thoughts

Example:
Input: "orange sticks for manicure"
CORRECT: "Orange sticks for manicure."
WRONG: "Orange sticks for manicure. They are used for shaping and caring for nails."

Output ONLY the original words with formatting. Nothing more."""


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
            Application-specific prompt, fallback prompt, or universal default if not set
        """
        # Special handling for _fallback
        if app_name == "_fallback":
            # Check if there's a custom fallback prompt
            if "_fallback" in self.app_prompts and self.app_prompts["_fallback"]:
                return self.app_prompts["_fallback"]
            # Use hardcoded fallback if no custom fallback is set
            return FALLBACK_FORMATTING_PROMPT
        
        # For known applications
        if app_name in self.applications:
            # Check if app has a custom prompt
            if app_name in self.app_prompts and self.app_prompts[app_name]:
                return self.app_prompts[app_name]
            # Use universal default for known apps without custom prompts
            return UNIVERSAL_DEFAULT_PROMPT
        
        # For unknown applications (not in applications list)
        # Use fallback prompt (check for custom fallback first)
        if "_fallback" in self.app_prompts and self.app_prompts["_fallback"]:
            return self.app_prompts["_fallback"]
        return FALLBACK_FORMATTING_PROMPT
    
    def set_prompt_for_app(self, app_name: str, prompt: str) -> None:
        """
        Set the prompt for a specific application.
        
        Args:
            app_name: Application name
            prompt: Prompt text (empty string to use default)
        """
        self.app_prompts[app_name] = prompt
    
    @classmethod
    def from_env(cls, env_path: Optional[str] = None) -> 'FormattingConfig':
        """
        Load formatting configuration from environment variables.
        
        Args:
            env_path: Path to .env file. If None, uses default path.
        
        Returns:
            FormattingConfig: Configuration loaded from environment
        """
        from core.config import get_env_path
        
        if env_path is None:
            env_path = str(get_env_path())
        
        # Load environment variables
        load_dotenv(env_path, override=True)
        
        # Parse enabled flag
        enabled_str = os.getenv("FORMATTING_ENABLED", "false").lower()
        enabled = enabled_str in ("true", "1", "yes")
        
        # Load provider and model
        provider = os.getenv("FORMATTING_PROVIDER", "groq").lower()
        model = os.getenv("FORMATTING_MODEL", "")
        
        # Load temperature (default 0.3 for consistent formatting)
        temperature_str = os.getenv("FORMATTING_TEMPERATURE", "0.3")
        try:
            temperature = float(temperature_str)
            temperature = max(0.0, min(1.0, temperature))  # Clamp to [0.0, 1.0]
        except ValueError:
            temperature = 0.3
        
        # Load optional system prompt (decode escaped newlines) - deprecated
        system_prompt = os.getenv("FORMATTING_SYSTEM_PROMPT", "")
        if system_prompt:
            system_prompt = system_prompt.replace('\\n', '\n')
        
        # Try to load new JSON format first
        app_prompts_json = os.getenv("FORMATTING_APP_PROMPTS", "")
        app_prompts = {}
        applications = []
        
        if app_prompts_json:
            # New format exists - parse JSON
            try:
                app_prompts_data = json.loads(app_prompts_json)
                applications = list(app_prompts_data.keys())
                # Extract prompts from JSON structure
                for app_name, app_config in app_prompts_data.items():
                    if isinstance(app_config, dict):
                        app_prompts[app_name] = app_config.get("prompt", "")
                    else:
                        # Fallback for simple format
                        app_prompts[app_name] = ""
            except json.JSONDecodeError:
                logger.warning("Failed to parse FORMATTING_APP_PROMPTS JSON, falling back to old format")
                app_prompts_json = ""
        
        if not app_prompts_json:
            # Fall back to old format or defaults
            applications_str = os.getenv("FORMATTING_APPLICATIONS", "")
            
            if not applications_str:
                # Use defaults (including _fallback)
                applications = ["notion", "obsidian", "markdown", "word", "libreoffice", "vscode", "_fallback"]
            else:
                applications = [
                    app.strip() 
                    for app in applications_str.split(",") 
                    if app.strip()
                ]
                # Always ensure _fallback is in the list
                if "_fallback" not in applications:
                    applications.append("_fallback")
            
            # Initialize empty prompts for all applications
            app_prompts = {app: "" for app in applications}
        
        # Ensure _fallback is always in applications list
        if "_fallback" not in applications:
            applications.append("_fallback")
            if "_fallback" not in app_prompts:
                app_prompts["_fallback"] = ""
        
        # Load custom provider settings
        custom_base_url = os.getenv("FORMATTING_CUSTOM_BASE_URL", "")
        custom_api_key = os.getenv("FORMATTING_CUSTOM_API_KEY", "")
        
        # Load web app keywords for browser detection
        web_app_keywords_json = os.getenv("FORMATTING_WEB_APP_KEYWORDS", "")
        web_app_keywords = {}
        
        if web_app_keywords_json:
            try:
                web_app_keywords = json.loads(web_app_keywords_json)
            except json.JSONDecodeError:
                logger.warning("Failed to parse FORMATTING_WEB_APP_KEYWORDS JSON, using defaults")
                web_app_keywords = {}
        
        # If no keywords loaded, use defaults from formatting_module
        if not web_app_keywords:
            # Import default mappings
            from services.formatting_module import BROWSER_TITLE_MAPPINGS
            web_app_keywords = {
                format_type: list(patterns)
                for format_type, patterns in BROWSER_TITLE_MAPPINGS.items()
            }
        
        return cls(
            enabled=enabled,
            provider=provider,
            model=model,
            applications=applications,
            temperature=temperature,
            system_prompt=system_prompt,
            app_prompts=app_prompts,
            custom_base_url=custom_base_url,
            custom_api_key=custom_api_key,
            web_app_keywords=web_app_keywords
        )
    
    def to_env(self) -> dict:
        """
        Convert configuration to environment variable format.
        
        Returns:
            dict: Dictionary of environment variable key-value pairs
        """
        # Build JSON structure for app_prompts
        app_prompts_data = {}
        for app_name in self.applications:
            app_prompts_data[app_name] = {
                "enabled": True,
                "prompt": self.app_prompts.get(app_name, "")
            }
        
        return {
            "FORMATTING_ENABLED": "true" if self.enabled else "false",
            "FORMATTING_PROVIDER": self.provider,
            "FORMATTING_MODEL": self.model,
            "FORMATTING_APP_PROMPTS": json.dumps(app_prompts_data, ensure_ascii=False),
            "FORMATTING_TEMPERATURE": str(self.temperature),
            "FORMATTING_CUSTOM_BASE_URL": self.custom_base_url,
            "FORMATTING_CUSTOM_API_KEY": self.custom_api_key,
            "FORMATTING_WEB_APP_KEYWORDS": json.dumps(self.web_app_keywords, ensure_ascii=False),
            # Keep old format for backward compatibility (but will be removed after migration)
            "FORMATTING_APPLICATIONS": ",".join(self.applications),
            "FORMATTING_SYSTEM_PROMPT": self.system_prompt
        }
    
    def save_to_env(self, env_path: Optional[str] = None) -> None:
        """
        Save configuration to .env file.
        
        Args:
            env_path: Path to .env file. If None, uses default path.
        """
        from core.config import get_env_path
        
        if env_path is None:
            env_path = str(get_env_path())
        
        # Convert to environment variables
        env_vars = self.to_env()
        
        # Read existing .env file
        env_lines = []
        if Path(env_path).exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
        
        # Update or add each key
        for key, value in env_vars.items():
            key_found = False
            for i, line in enumerate(env_lines):
                line_stripped = line.strip()
                # Skip comments and empty lines
                if line_stripped and not line_stripped.startswith('#'):
                    if '=' in line_stripped:
                        existing_key = line_stripped.split('=')[0].strip()
                        if existing_key == key:
                            env_lines[i] = f"{key}={value}\n"
                            key_found = True
                            break
            
            # If key not found, add to end
            if not key_found:
                # Add empty line before new key if file not empty
                if env_lines and not env_lines[-1].endswith('\n'):
                    env_lines.append('\n')
                env_lines.append(f"{key}={value}\n")
        
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
