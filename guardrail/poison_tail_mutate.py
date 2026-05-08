from copy import deepcopy
from typing import Any, Dict
from entities import InputGuardrailRequest


def poison_tail_mutate(request: InputGuardrailRequest) -> Dict[str, Any]:
    """
    Mutate input request:
    For every user message, if it contains 'poison' (case-insensitive),
    mask everything after the word 'poison' with '*'.
    """
    req_body = deepcopy(request.requestBody or {})
    messages = req_body.get("messages", [])

    mutated = False

    for msg in messages:
        if msg.get("role") != "user":
            continue

        content = msg.get("content", "")
        if not isinstance(content, str):
            continue

        lower = content.lower()
        idx = lower.find("poison")
        if idx == -1:
            continue

        start = idx + len("poison")
        tail = content[start:]
        if tail:
            msg["content"] = content[:start] + ("*" * len(tail))
            mutated = True

    return {
        "verdict": True,
        "transformed": mutated,
        "result": req_body,
        "message": "Poison tail masked" if mutated else "No poison keyword found",
        "details": {"keyword": "poison", "mutated": mutated},
    }