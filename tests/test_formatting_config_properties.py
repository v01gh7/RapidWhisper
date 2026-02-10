"""
Property-based tests for FormattingConfig data model.
"""

import pytest
from hypothesis import given, strategies as st
from services.formatting_config import FormattingConfig, UNIVERSAL_DEFAULT_PROMPT


app_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
    min_size=1,
    max_size=50
)

prompts = st.text(max_size=10000)


@given(
    apps_with_prompts=st.lists(
        st.tuples(app_names, prompts),
        min_size=1,
        max_size=20,
        unique_by=lambda x: x[0]
    )
)
def test_property_9_unique_prompt_storage(apps_with_prompts):
    """Property 9: Unique Prompt Storage - Validates: Requirements 5.1, 5.3"""
    config = FormattingConfig()
    
    # Add all apps to applications list so they're treated as known apps
    config.applications = [app_name for app_name, _ in apps_with_prompts]
    
    for app_name, prompt in apps_with_prompts:
        config.set_prompt_for_app(app_name, prompt)
    
    for app_name, expected_prompt in apps_with_prompts:
        retrieved_prompt = config.get_prompt_for_app(app_name)
        
        if expected_prompt:
            assert retrieved_prompt == expected_prompt
        else:
            assert retrieved_prompt == UNIVERSAL_DEFAULT_PROMPT


@given(app_name=app_names.filter(lambda x: x != "_fallback"))
def test_property_10_default_prompt_assignment(app_name):
    """Property 10: Default Prompt Assignment - Validates: Requirements 5.2, 6.2"""
    config = FormattingConfig()
    
    # Add app to applications list so it's treated as a known app
    config.applications = [app_name]
    
    config.set_prompt_for_app(app_name, "")
    
    retrieved_prompt = config.get_prompt_for_app(app_name)
    assert retrieved_prompt == UNIVERSAL_DEFAULT_PROMPT


@given(app_name=app_names, custom_prompt=prompts.filter(lambda x: len(x) > 0))
def test_property_11_correct_prompt_retrieval(app_name, custom_prompt):
    """Property 11: Correct Prompt Retrieval - Validates: Requirements 5.4"""
    config = FormattingConfig()
    
    # Add app to applications list so it's treated as a known app
    config.applications = [app_name]
    
    config.set_prompt_for_app(app_name, custom_prompt)
    
    retrieved_prompt = config.get_prompt_for_app(app_name)
    assert retrieved_prompt == custom_prompt


def test_default_model_for_zai_provider():
    """FormattingConfig should return a non-empty default model for Z.AI provider."""
    config = FormattingConfig(provider="zai", model="")
    assert config.get_model() == "GLM-4.7"


def test_is_valid_accepts_zai_provider():
    """FormattingConfig validation should treat Z.AI as a valid provider."""
    config = FormattingConfig(
        provider="zai",
        model="",
        applications=["_fallback"],
        temperature=0.3,
    )
    assert config.is_valid()
