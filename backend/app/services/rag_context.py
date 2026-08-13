"""Pure helpers for turning retrieved chunks into LLM-safe evidence context."""
import os
import re
from typing import Any, Dict, List, Optional


def build_context(citations: List[Dict[str, Any]], max_chars: Optional[int] = None) -> str:
    """Build a compact, non-redundant evidence set for the generation model."""
    max_chars = max_chars or int(os.getenv("RAG_MAX_CONTEXT_CHARS", "14000"))
    max_sources = int(os.getenv("RAG_MAX_CONTEXT_SOURCES", "6"))
    parts, seen, seen_word_sets, used = [], set(), [], 0
    for number, citation in enumerate(citations, start=1):
        snippet = (citation.get("snippet") or "").strip()
        if not snippet or snippet in seen:
            continue
        snippet_words = set(re.findall(r"\w+", snippet.lower()))
        if any(
            snippet_words and len(snippet_words & previous) / len(snippet_words | previous) >= 0.75
            for previous in seen_word_sets
        ):
            continue
        title = citation.get("documentTitle", "Unknown Document")
        page = citation.get("page", 1)
        remaining = max_chars - used
        header = f"[Source {number}] {title}, page {page}\n"
        if remaining <= len(header):
            break
        entry = f"{header}{snippet[:min(3000, remaining - len(header))]}"
        parts.append(entry)
        seen.add(snippet)
        seen_word_sets.append(snippet_words)
        used += len(entry) + 2
        if len(parts) >= max_sources:
            break
    return "\n\n".join(parts)
