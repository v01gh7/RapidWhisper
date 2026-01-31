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
    
    for app_name, prompt in apps_with_prompts:
        config.set_prompt_for_app(app_name, prompt)
    
    for app_name, expected_prompt in apps_with_prompts:
        retrieved_prompt = config.get_prompt_for_app(app_name)
        
        if expected_prompt:
            assert retrieved_prompt == expected_prompt
        else:
            assert retrieved_prompt == UNIVERSAL_DEFAULT_PROMPT


@given(app_name=app_names)
def test_property_10_default_prompt_assignment(app_name):
    """Property 10: Default Prompt Assignment - Validates: Requirements 5.2, 6.2"""
    config = FormattingConfig()
    config.set_prompt_for_app(app_name, "")
    
    retrieved_prompt = config.get_prompt_for_app(app_name)
    assert retrieved_prompt == UNIVERSAL_DEFAULT_PROMPT


@given(app_name=app_names, custom_prompt=prompts.filter(lambda x: len(x) > 0))
def test_property_11_correct_prompt_retrieval(app_name, custom_prompt):
    """Property 11: Correct Prompt Retrieval - Validates: Requirements 5.4"""
    config = FormattingConfig()
    config.set_prompt_for_app(app_name, custom_prompt)
    
    retrieved_prompt = config.get_prompt_for_app(app_name)
    assert retrieved_prompt == custom_prompt
