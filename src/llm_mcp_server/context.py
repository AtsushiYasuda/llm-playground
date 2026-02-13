"""Context optimization utilities: caching, truncation, and token estimation."""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Rough token count: ~4 chars per token for English, ~1.5 for CJK-heavy text."""
    cjk = sum(1 for c in text if "\u3000" <= c <= "\u9fff" or "\uf900" <= c <= "\ufaff")
    ratio = 1.5 if cjk > len(text) * 0.3 else 4.0
    return max(1, int(len(text) / ratio))


# ---------------------------------------------------------------------------
# Response truncation
# ---------------------------------------------------------------------------

_TRUNCATION_NOTICE = "\n\n[... truncated — {removed} chars omitted]"


def truncate(text: str, max_chars: int) -> str:
    """Hard-truncate *text* at a word boundary, appending a notice if cut."""
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0] or text[:max_chars]
    removed = len(text) - len(cut)
    logger.info("Truncated response: %d -> %d chars", len(text), len(cut))
    return cut + _TRUNCATION_NOTICE.format(removed=removed)


# ---------------------------------------------------------------------------
# TTL cache for LLM responses
# ---------------------------------------------------------------------------

@dataclass
class _CacheEntry:
    value: str
    expires_at: float


@dataclass
class ResponseCache:
    """Simple in-memory TTL cache keyed by prompt hash."""

    ttl: float = 300.0
    _store: dict[str, _CacheEntry] = field(default_factory=dict)

    def _key(self, prompt: str, system_prompt: str, model: str) -> str:
        raw = f"{model}|{system_prompt}|{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, prompt: str, system_prompt: str, model: str) -> str | None:
        key = self._key(prompt, system_prompt, model)
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            return None
        logger.info("Cache hit (key=%s…)", key[:8])
        return entry.value

    def put(self, prompt: str, system_prompt: str, model: str, value: str) -> None:
        key = self._key(prompt, system_prompt, model)
        self._store[key] = _CacheEntry(value=value, expires_at=time.monotonic() + self.ttl)
        self._evict()

    def _evict(self) -> None:
        """Remove expired entries (lazy sweep)."""
        now = time.monotonic()
        expired = [k for k, v in self._store.items() if now > v.expires_at]
        for k in expired:
            del self._store[k]

    @property
    def size(self) -> int:
        return len(self._store)
