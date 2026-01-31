"""
Migration script: .env -> config.jsonc + prompt files

This script migrates all settings from .env file to:
1. config.jsonc - main configuration file with comments
2. config/prompts/*.txt - individual prompt files for each application

Usage:
    python migrate_to_jsonc.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

def load_env_file(env_path=".env"):
    """Load .env file and return all variables as dict"""
    load_dotenv(env_path, override=True)
    
    config = {}
    secrets = {}
    
    # AI Provider Configuration
    secrets["api_keys"] = {
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "groq": os.getenv("GROQ_API_KEY", ""),
        "glm": os.getenv("GLM_API_KEY", "")
    }
    
    secrets["custom_providers"] = {
        "api_key": os.getenv("CUSTOM_API_KEY", ""),
        "formatting_api_key": os.getenv("FORMATTING_CUSTOM_API_KEY", "")
    }
    
    config["ai_provider"] = {
        "provider": os.getenv("AI_PROVIDER", "groq"),
        "custom": {
            "base_url": os.getenv("CUSTOM_BASE_URL", "http://localhost:1234/v1/"),
            "model": os.getenv("CUSTOM_MODEL", "whisper-1")
        }
    }
    
    # Application Settings
    config["application"] = {
        "app_user_model_id": os.getenv("APP_USER_MODEL_ID", "RapidWhisper"),
        "hotkey": os.getenv("HOTKEY", "ctrl+space")
    }
    
    # Audio Settings
    config["audio"] = {
        "silence_threshold": float(os.getenv("SILENCE_THRESHOLD", "0.02")),
        "silence_duration": float(os.getenv("SILENCE_DURATION", "1.5")),
        "silence_padding": int(os.getenv("SILENCE_PADDING", "650")),
        "sample_rate": int(os.getenv("SAMPLE_RATE", "16000")),
        "chunk_size": int(os.getenv("CHUNK_SIZE", "1024")),
        "manual_stop": os.getenv("MANUAL_STOP", "false").lower() == "true"
    }
    
    # Window Settings
    pos_x = os.getenv("WINDOW_POSITION_X", "")
    pos_y = os.getenv("WINDOW_POSITION_Y", "")
    
    config["window"] = {
        "width": int(os.getenv("WINDOW_WIDTH", "400")),
        "height": int(os.getenv("WINDOW_HEIGHT", "120")),
        "opacity": int(os.getenv("WINDOW_OPACITY", "100")),
        "auto_hide_delay": float(os.getenv("AUTO_HIDE_DELAY", "2.5")),
        "remember_position": os.getenv("REMEMBER_WINDOW_POSITION", "true").lower() == "true",
        "position_preset": os.getenv("WINDOW_POSITION_PRESET", "center"),
        "position_x": int(pos_x) if pos_x else None,
        "position_y": int(pos_y) if pos_y else None,
        "font_sizes": {
            "floating_main": int(os.getenv("FONT_SIZE_FLOATING_MAIN", "14")),
            "floating_info": int(os.getenv("FONT_SIZE_FLOATING_INFO", "12")),
            "settings_labels": int(os.getenv("FONT_SIZE_SETTINGS_LABELS", "11")),
            "settings_titles": int(os.getenv("FONT_SIZE_SETTINGS_TITLES", "16"))
        }
    }
    
    # Recording Settings
    config["recording"] = {
        "keep_recordings": os.getenv("KEEP_RECORDINGS", "false").lower() == "true",
        "recordings_path": os.getenv("RECORDINGS_PATH", "")
    }
    
    # Post-Processing Settings
    config["post_processing"] = {
        "enabled": os.getenv("ENABLE_POST_PROCESSING", "false").lower() == "true",
        "provider": os.getenv("POST_PROCESSING_PROVIDER", "groq"),
        "model": os.getenv("POST_PROCESSING_MODEL", "llama-3.3-70b-versatile"),
        "custom_model": os.getenv("POST_PROCESSING_CUSTOM_MODEL", ""),
        "prompt": os.getenv("POST_PROCESSING_PROMPT", "You are a text editor. Your task: fix grammatical errors, add punctuation and improve text readability. Preserve the original meaning and style. Don't add anything extra. Return only the corrected text without comments."),
        "glm_use_coding_plan": os.getenv("GLM_USE_CODING_PLAN", "false").lower() == "true",
        "llm": {
            "base_url": os.getenv("LLM_BASE_URL", "http://localhost:1234/v1/"),
            "api_key": os.getenv("LLM_API_KEY", "local")
        }
    }
    
    # Localization Settings
    config["localization"] = {
        "language": os.getenv("INTERFACE_LANGUAGE", "en")
    }
    
    # Logging Settings
    config["logging"] = {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "file": os.getenv("LOG_FILE", "rapidwhisper.log")
    }
    
    # About Section
    config["about"] = {
        "github_url": os.getenv("GITHUB_URL", "https://github.com/yourusername/rapidwhisper"),
        "docs_url": os.getenv("DOCS_URL", "https://github.com/yourusername/rapidwhisper/tree/main/docs")
    }
    
    # Formatting Settings
    formatting_enabled = os.getenv("FORMATTING_ENABLED", "false").lower() == "true"
    formatting_provider = os.getenv("FORMATTING_PROVIDER", "groq")
    formatting_model = os.getenv("FORMATTING_MODEL", "")
    formatting_temp = float(os.getenv("FORMATTING_TEMPERATURE", "0.3"))
    
    # Load web app keywords
    web_keywords_json = os.getenv("FORMATTING_WEB_APP_KEYWORDS", "{}")
    try:
        web_keywords = json.loads(web_keywords_json)
    except json.JSONDecodeError:
        print("Warning: Failed to parse FORMATTING_WEB_APP_KEYWORDS, using empty dict")
        web_keywords = {}
    
    # Load app prompts
    app_prompts_json = os.getenv("FORMATTING_APP_PROMPTS", "{}")
    app_prompts_data = {}
    try:
        # Read directly from file to avoid dotenv breaking JSON
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('FORMATTING_APP_PROMPTS='):
                        app_prompts_json = line.split('=', 1)[1].strip()
                        break
        app_prompts_data = json.loads(app_prompts_json)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse FORMATTING_APP_PROMPTS: {e}")
        app_prompts_data = {}
    
    config["formatting"] = {
        "enabled": formatting_enabled,
        "provider": formatting_provider,
        "model": formatting_model,
        "temperature": formatting_temp,
        "custom": {
            "base_url": os.getenv("FORMATTING_CUSTOM_BASE_URL", "http://localhost:1234/v1/")
        },
        "web_app_keywords": web_keywords,
        "app_prompts": {}  # Will be filled with file paths
    }
    
    return config, app_prompts_data, secrets


def save_prompts_to_files(app_prompts_data, prompts_dir="config/prompts"):
    """Save each application's prompt to a separate file"""
    # Create prompts directory
    Path(prompts_dir).mkdir(parents=True, exist_ok=True)
    
    prompt_files = {}
    
    for app_name, app_config in app_prompts_data.items():
        if isinstance(app_config, dict):
            prompt = app_config.get("prompt", "")
        else:
            prompt = ""
        
        # Decode \\n to actual newlines
        if prompt:
            prompt = prompt.replace('\\n', '\n')
        
        # Save to file
        file_path = f"{prompts_dir}/{app_name}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        prompt_files[app_name] = file_path
        print(f"✓ Saved prompt for '{app_name}' to {file_path}")
    
    return prompt_files


def save_secrets_to_json(secrets, output_path="secrets.json"):
    """Save secrets to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(secrets, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved secrets to {output_path}")
    print(f"  ⚠️  IMPORTANT: Add {output_path} to .gitignore!")


def save_config_to_jsonc(config, output_path="config.jsonc"):
    """Save configuration to JSONC file with comments"""
    # Convert to JSON with indentation
    json_str = json.dumps(config, indent=2, ensure_ascii=False)
    
    # Add comments (simple approach - prepend comment block)
    header = """// ============================================
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
// ============================================

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + json_str)
    
    print(f"✓ Saved configuration to {output_path}")


def main():
    """Main migration function"""
    print("=" * 60)
    print("RapidWhisper: Migrating .env to config.jsonc + secrets.json")
    print("=" * 60)
    print()
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("Error: .env file not found!")
        return
    
    print("Step 1: Loading .env file...")
    config, app_prompts_data, secrets = load_env_file(".env")
    print("✓ Loaded configuration from .env")
    print()
    
    print("Step 2: Saving secrets to secrets.json...")
    save_secrets_to_json(secrets, "secrets.json")
    print()
    
    print("Step 3: Saving prompts to separate files...")
    prompt_files = save_prompts_to_files(app_prompts_data)
    config["formatting"]["app_prompts"] = prompt_files
    print()
    
    print("Step 4: Saving configuration to config.jsonc...")
    save_config_to_jsonc(config, "config.jsonc")
    print()
    
    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review config.jsonc and config/prompts/*.txt files")
    print("2. Review secrets.json (contains API keys)")
    print("3. Add secrets.json to .gitignore (IMPORTANT!)")
    print("4. Update code to read from config.jsonc instead of .env")
    print("5. Keep .env as backup until migration is complete")
    print()


if __name__ == "__main__":
    main()
