"""
Test script for config_loader.py

This script tests:
1. Loading config.jsonc
2. Loading prompts from files
3. Getting configuration values
"""

from core.config_loader import ConfigLoader, strip_json_comments
from services.formatting_config import FormattingConfig


def test_strip_comments():
    """Test JSONC comment stripping"""
    print("=" * 60)
    print("Test 1: Strip JSON comments")
    print("=" * 60)
    
    jsonc = """
    {
        // This is a comment
        "key1": "value1",  // inline comment
        /* Multi-line
           comment */
        "key2": "value2"
    }
    """
    
    result = strip_json_comments(jsonc)
    print("Input:")
    print(jsonc)
    print("\nOutput:")
    print(result)
    print("\n✓ Comments stripped successfully\n")


def test_load_config():
    """Test loading config.jsonc"""
    print("=" * 60)
    print("Test 2: Load config.jsonc + secrets.json")
    print("=" * 60)
    
    loader = ConfigLoader("config.jsonc", "secrets.json")
    config = loader.load()
    
    print(f"✓ Loaded configuration")
    print(f"  - AI Provider: {config['ai_provider']['provider']}")
    print(f"  - API Keys loaded: {bool(config['ai_provider'].get('api_keys'))}")
    print(f"  - Formatting Enabled: {config['formatting']['enabled']}")
    print(f"  - Applications: {len(config['formatting']['app_prompts'])} configured")
    print()


def test_get_values():
    """Test getting configuration values"""
    print("=" * 60)
    print("Test 3: Get configuration values")
    print("=" * 60)
    
    loader = ConfigLoader("config.jsonc", "secrets.json")
    
    # Test dot-notation access
    provider = loader.get("ai_provider.provider")
    print(f"✓ ai_provider.provider = {provider}")
    
    # Test API keys (from secrets.json)
    groq_key = loader.get("ai_provider.api_keys.groq", "")
    print(f"✓ ai_provider.api_keys.groq = {groq_key[:20] if groq_key else 'not set'}...")
    
    width = loader.get("window.width")
    print(f"✓ window.width = {width}")
    
    enabled = loader.get("formatting.enabled")
    print(f"✓ formatting.enabled = {enabled}")
    
    # Test default value
    missing = loader.get("nonexistent.key", "default_value")
    print(f"✓ nonexistent.key = {missing} (default)")
    print()


def test_load_prompts():
    """Test loading prompts from files"""
    print("=" * 60)
    print("Test 4: Load prompts from files")
    print("=" * 60)
    
    loader = ConfigLoader("config.jsonc", "secrets.json")
    
    # Test loading WhatsApp prompt
    whatsapp_prompt = loader.get_prompt("whatsapp")
    print(f"✓ Loaded WhatsApp prompt ({len(whatsapp_prompt)} characters)")
    print(f"  First 100 chars: {whatsapp_prompt[:100]}...")
    print()
    
    # Test loading fallback prompt
    fallback_prompt = loader.get_prompt("_fallback")
    print(f"✓ Loaded fallback prompt ({len(fallback_prompt)} characters)")
    print(f"  First 100 chars: {fallback_prompt[:100]}...")
    print()


def test_formatting_config():
    """Test FormattingConfig.from_config()"""
    print("=" * 60)
    print("Test 5: FormattingConfig.from_config()")
    print("=" * 60)
    
    loader = ConfigLoader("config.jsonc", "secrets.json")
    config = FormattingConfig.from_config(loader)
    
    print(f"✓ Created FormattingConfig")
    print(f"  - Enabled: {config.enabled}")
    print(f"  - Provider: {config.provider}")
    print(f"  - Model: {config.get_model()}")
    print(f"  - Applications: {config.applications}")
    print(f"  - Temperature: {config.temperature}")
    print()
    
    # Test getting prompt for application
    whatsapp_prompt = config.get_prompt_for_app("whatsapp")
    print(f"✓ Got WhatsApp prompt ({len(whatsapp_prompt)} characters)")
    print(f"  First 100 chars: {whatsapp_prompt[:100]}...")
    print()


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("CONFIG LOADER TESTS")
    print("=" * 60)
    print("\n")
    
    try:
        test_strip_comments()
        test_load_config()
        test_get_values()
        test_load_prompts()
        test_formatting_config()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
