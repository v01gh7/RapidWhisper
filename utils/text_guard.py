"""
Utilities to validate formatted text output.
"""

from __future__ import annotations

import re
from typing import List

_WORD_RE = re.compile(r"[\w]+", flags=re.UNICODE)
_BBCODE_TAG_RE = re.compile(r"\[(?:/?[a-z][a-z0-9_]*)(?:=[^\]]+)?\]", flags=re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"</?[a-z][^>]*>", flags=re.IGNORECASE)
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^)]+)\)")

# Common markup/control words that can appear in malformed formatted output.
_FORMATTING_TOKENS = {
    "b",
    "i",
    "u",
    "s",
    "size",
    "color",
    "font",
    "url",
    "img",
    "list",
    "quote",
    "code",
    "center",
    "left",
    "right",
    "justify",
    "spoiler",
    "table",
    "tr",
    "td",
    "th",
    "ul",
    "ol",
    "li",
    "div",
    "span",
    "p",
    "br",
    "strong",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}


def _strip_markup(text: str) -> str:
    """Remove common markup wrappers before token comparison."""
    if not text:
        return ""
    normalized = _MD_LINK_RE.sub(r"\1", text)
    normalized = _BBCODE_TAG_RE.sub(" ", normalized)
    normalized = _HTML_TAG_RE.sub(" ", normalized)
    return normalized


def _tokenize(text: str) -> List[str]:
    normalized = _strip_markup(text)
    return [token.lower() for token in _WORD_RE.findall(normalized)]


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
        if token in _FORMATTING_TOKENS:
            continue
        if token not in original_tokens:
            return True
    return False
