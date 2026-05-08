from copy import deepcopy
from typing import Any, Dict, List, Tuple

from entities import InputGuardrailRequest

DEFAULT_KEYWORD = "poison"
DEFAULT_MASK_CHAR = "*"


def _mask_after_keyword(text: str, keyword: str, mask_char: str = DEFAULT_MASK_CHAR) -> Tuple[str, bool]:
    lower = text.lower()
    idx = lower.find(keyword.lower())
    if idx == -1:
        return text, False

    start = idx + len(keyword)
    tail = text[start:]
    if not tail:
        return text, False

    return text[:start] + (mask_char * len(tail)), True


def poison_tail_mutate(request: InputGuardrailRequest) -> Dict[str, Any]:
    """
    Mutate input request:
    For each user message, if it contains the keyword (default: "poison"),
    mask everything after that keyword with '*' characters.

    Returns a custom-guardrail mutate contract:
      - transformed=True only when a mutation is actually applied
      - result=<mutated request body>
    """
    keyword = (request.config or {}).get("keyword", DEFAULT_KEYWORD)
    mask_char = (request.config or {}).get("mask_char", DEFAULT_MASK_CHAR)

    req_body: Dict[str, Any] = deepcopy(request.requestBody or {})
    messages: List[Dict[str, Any]] = req_body.get("messages", [])

    mutated = False
    mutated_message_indices: List[int] = []

    for i, msg in enumerate(messages):
        if msg.get("role") != "user":
            continue

        content = msg.get("content")

        # Standard text content
        if isinstance(content, str):
            new_content, changed = _mask_after_keyword(content, keyword, mask_char)
            if changed:
                msg["content"] = new_content
                mutated = True
                mutated_message_indices.append(i)
            continue

        # Multimodal content array support (OpenAI-style parts)
        if isinstance(content, list):
            changed_any_part = False
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "text" and isinstance(part.get("text"), str):
                    new_text, changed = _mask_after_keyword(part["text"], keyword, mask_char)
                    if changed:
                        part["text"] = new_text
                        changed_any_part = True
            if changed_any_part:
                mutated = True
                mutated_message_indices.append(i)

    return {
        "verdict": True,
        "transformed": mutated,
        "result": req_body,
        "message": "Poison tail masked" if mutated else "No poison keyword found",
        "details": {
            "keyword": keyword,
            "mutated": mutated,
            "mutated_message_indices": mutated_message_indices,
        },
    }