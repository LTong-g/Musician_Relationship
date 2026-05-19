from __future__ import annotations
import hashlib
from typing import Any


def normalize_avatar_url(value: Any) -> str:
    url = str(value or "").strip()
    if url.startswith("http://"):
        return "https://" + url.removeprefix("http://")
    return url


def avatar_key(value: Any) -> str:
    url = normalize_avatar_url(value)
    if not url:
        return ""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()
