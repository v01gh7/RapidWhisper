"""
Configuration Saver for JSONC format

This module saves configuration to config.jsonc and secrets.json files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger()


class ConfigSaver:
    """
    Configuration saver for JSONC format.
    
    Saves configuration to:
    1. config.jsonc - main configuration (public)
    2. secrets.json - API keys and sensitive data (private)
    3. config/prompts/*.txt - formatting prompts (public)
    """
    
    def __init__(self, config_path: str = None, secrets_path: str = None):
        """
        Initialize configuration saver.
        
        Args:
            config_path: Path to config.jsonc file (if None, uses get_config_dir())
            secrets_path: Path to secrets.json file (if None, uses get_config_dir())
        """
        from core.config import get_config_dir
        
        config_dir = get_config_dir()
        
        if config_path is None:
            self.config_path = str(config_dir / "config.jsonc")
        else:
            self.config_path = config_path
            
        if secrets_path is None:
            self.secrets_path = str(config_dir / "secrets.json")
        else:
            self.secrets_path = secrets_path
    
    def save_config(self, config: Dict[str, Any]):
        """
        Save configuration to config.jsonc.
        
        Args:
            config: Configuration dictionary
        """
        try:
            # Read existing config to preserve comments
            header = self._read_header()
            
            # Convert to JSON
            json_str = json.dumps(config, indent=2, ensure_ascii=False)
            
            # Write with header
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(header)
                f.write(json_str)
            
            logger.info(f"✓ Saved configuration to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def save_secrets(self, secrets: Dict[str, Any]):
        """
        Save secrets to secrets.json.
        
        Args:
            secrets: Secrets dictionary
        """
        try:
            with open(self.secrets_path, 'w', encoding='utf-8') as f:
                json.dump(secrets, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved secrets to {self.secrets_path}")
            
        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")
            raise
    
    def save_prompt(self, app_name: str, prompt: str, prompts_dir: str = None):
        """
        Save prompt to file.
        
        Args:
            app_name: Application name
            prompt: Prompt text
            prompts_dir: Directory for prompts (if None, uses get_config_dir()/config/prompts)
        """
        try:
            from core.config import get_config_dir
            
            # Use config directory if prompts_dir not specified
            if prompts_dir is None:
                config_dir = get_config_dir()
                prompts_dir = config_dir / "config" / "prompts"
            else:
                prompts_dir = Path(prompts_dir)
            
            # Create directory if needed
            prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt
            prompt_file = prompts_dir / f"{app_name}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            logger.info(f"✓ Saved prompt for '{app_name}' to {prompt_file}")
            
        except Exception as e:
            logger.error(f"Failed to save prompt for '{app_name}': {e}")
            raise
    
    def update_value(self, key_path: str, value: Any):
        """
        Update a single value in config.jsonc.
        
        Args:
            key_path: Dot-separated path to value (e.g., "window.width")
            value: New value
        """
        try:
            # Load current config
            from core.config_loader import load_jsonc
            config = load_jsonc(self.config_path)
            
            # Update value
            keys = key_path.split('.')
            current = config
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            current[keys[-1]] = value
            
            # Save
            self.save_config(config)
            
            logger.info(f"✓ Updated {key_path} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to update {key_path}: {e}")
            raise
    
    def update_multiple_values(self, updates: Dict[str, Any]):
        """
        Update multiple values in config.jsonc at once.
        More efficient than calling update_value multiple times.
        
        Args:
            updates: Dictionary of key_path -> value pairs
        """
        try:
            # Load current config
            from core.config_loader import load_jsonc
            config = load_jsonc(self.config_path)
            
            # Update all values
            for key_path, value in updates.items():
                keys = key_path.split('.')
                current = config
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                current[keys[-1]] = value
            
            # Save once
            self.save_config(config)
            
            logger.info(f"✓ Updated {len(updates)} values in config")
            
        except Exception as e:
            logger.error(f"Failed to update multiple values: {e}")
            raise
    
    def update_secret(self, key_path: str, value: str):
        """
        Update a single secret in secrets.json.
        
        Args:
            key_path: Dot-separated path to secret (e.g., "api_keys.groq")
            value: New secret value
        """
        try:
            # Load current secrets
            if os.path.exists(self.secrets_path):
                with open(self.secrets_path, 'r', encoding='utf-8') as f:
                    secrets = json.load(f)
            else:
                secrets = {"api_keys": {}, "custom_providers": {}}
            
            # Update value
            keys = key_path.split('.')
            current = secrets
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            current[keys[-1]] = value
            
            # Save
            self.save_secrets(secrets)
            
            logger.info(f"✓ Updated secret {key_path}")
            
        except Exception as e:
            logger.error(f"Failed to update secret {key_path}: {e}")
            raise
    
    def _read_header(self) -> str:
        """
        Read header comments from existing config.jsonc.
        
        Returns:
            Header string with comments
        """
        if not os.path.exists(self.config_path):
            return """// ============================================
// RapidWhisper Configuration File
// ============================================
// This file contains all application settings
// 
// Format: JSONC (JSON with Comments)
// - You can add comments using // or /* */
// - Trailing commas are allowed
//
// Formatting prompts are stored in separate files:
// - config/prompts/*.txt
//
// API keys are stored in secrets.json (not in git)
//
// ============================================

"""
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = []
                for line in f:
                    stripped = line.strip()
                    # Stop at first non-comment line
                    if stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
                        break
                    lines.append(line)
                
                return ''.join(lines)
        except:
            return ""


# Global saver instance
_config_saver = None


def get_config_saver() -> ConfigSaver:
    """Get global configuration saver instance"""
    global _config_saver
    if _config_saver is None:
        _config_saver = ConfigSaver()
    return _config_saver
