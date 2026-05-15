from __future__ import annotations

import re
import unicodedata


_ELLIPSIS_RE = re.compile(r"(?:\.\s*){3,}|(?:…\s*)+")
_WHITESPACE_RE = re.compile(r"\s+")
_OPEN_BRACKET_SPACE_RE = re.compile(r"([\(\[\{（【《「『])\s+")
_CLOSE_BRACKET_SPACE_RE = re.compile(r"\s+([\)\]\}）】》」』])")
_PUNCTUATION_AROUND_SPACE_RE = re.compile(r"\s*([,，、;；:：/／&＆+＋])\s*")
_HYPHEN_AROUND_SPACE_RE = re.compile(r"\s*([-‐‑‒–—―])\s*")
_FEAT_RE = re.compile(r"\b(?:feat|ft|featuring)\s*\.?\s*", re.IGNORECASE)

_PUNCTUATION_TRANSLATION = str.maketrans(
    {
        "，": ",",
        "。": ".",
        "．": ".",
        "、": ",",
        "；": ";",
        "：": ":",
        "！": "!",
        "？": "?",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "「": "[",
        "」": "]",
        "『": "[",
        "』": "]",
        "《": "<",
        "》": ">",
        "／": "/",
        "＆": "&",
        "＋": "+",
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
        "―": "-",
        "·": ".",
        "・": ".",
    }
)


def normalize_song_title_identity(value: str) -> str:
    """Return a conservative identity key for comparing song titles."""

    text = unicodedata.normalize("NFKC", value or "")
    text = text.translate(_PUNCTUATION_TRANSLATION)
    text = _ELLIPSIS_RE.sub("...", text)
    text = _FEAT_RE.sub("feat.", text)
    text = _WHITESPACE_RE.sub(" ", text)
    text = _OPEN_BRACKET_SPACE_RE.sub(r"\1", text)
    text = _CLOSE_BRACKET_SPACE_RE.sub(r"\1", text)
    text = _PUNCTUATION_AROUND_SPACE_RE.sub(r"\1", text)
    text = _HYPHEN_AROUND_SPACE_RE.sub(r"\1", text)
    return text.casefold().strip()
