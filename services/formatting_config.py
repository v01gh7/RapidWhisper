"""
Configuration module for transcription formatting feature.

This module provides the FormattingConfig dataclass for managing
formatting settings including AI provider, model, and target applications.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv, set_key


@dataclass
class FormattingConfig:
    """
    Formatting configuration data model.
    
    Attributes:
        enabled: Whether formatting is enabled
        provider: AI provider for formatting (groq, openai, glm, custom)
        model: Model name for formatting
        applications: List of application names to format for
        temperature: Temperature for AI model (0.0-1.0, lower = more deterministic)
        system_prompt: System prompt for formatting (optional override)
    """
    
    enabled: bool = False
    provider: str = "groq"  # groq, openai, glm, custom
    model: str = ""
    applications: List[str] = field(default_factory=list)
    temperature: float = 0.3  # Lower temperature for more consistent formatting
    system_prompt: str = ""  # Optional custom system prompt
    
    def is_valid(self) -> bool:
        """
        Validate configuration completeness.
        
        Returns:
            bool: True if configuration is valid and complete
        """
        return (
            self.provider in ["groq", "openai", "glm", "custom"] and
            bool(self.model) and
            bool(self.applications) and
            0.0 <= self.temperature <= 1.0
        )
    
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
        
        # Load optional system prompt (decode escaped newlines)
        system_prompt = os.getenv("FORMATTING_SYSTEM_PROMPT", "")
        if system_prompt:
            system_prompt = system_prompt.replace('\\n', '\n')
        
        # Parse applications list (comma-separated)
        applications_str = os.getenv("FORMATTING_APPLICATIONS", "")
        
        # If no applications configured, use defaults
        if not applications_str:
            applications = ["notion", "obsidian", "markdown", "word", "libreoffice", "vscode"]
        else:
            applications = [
                app.strip() 
                for app in applications_str.split(",") 
                if app.strip()
            ]
        
        return cls(
            enabled=enabled,
            provider=provider,
            model=model,
            applications=applications,
            temperature=temperature,
            system_prompt=system_prompt
        )
    
    def to_env(self) -> dict:
        """
        Convert configuration to environment variable format.
        
        Returns:
            dict: Dictionary of environment variable key-value pairs
        """
        return {
            "FORMATTING_ENABLED": "true" if self.enabled else "false",
            "FORMATTING_PROVIDER": self.provider,
            "FORMATTING_MODEL": self.model,
            "FORMATTING_APPLICATIONS": ",".join(self.applications),
            "FORMATTING_TEMPERATURE": str(self.temperature),
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
