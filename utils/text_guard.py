"""
Utilities to validate formatted text output.
"""

from __future__ import annotations

import re
from typing import List

_WORD_RE = re.compile(r"[\w]+", flags=re.UNICODE)


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in _WORD_RE.findall(text)]


def has_extra_tokens(original: str, candidate: str) -> bool:
    """
    Return True if candidate contains word tokens not present in original.

    Notes:
    - Case-insensitive comparison.
    - Pure numeric tokens are ignored to allow list numbering.
    """
    original_tokens = set(_tokenize(original))
    if not original_tokens:
        return False
    for token in _tokenize(candidate):
        if token.isdigit():
            continue
        if token not in original_tokens:
            return True
    return False
