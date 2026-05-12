"""Request (input) mutate: replace occurrences of 'poison' or 'bomb' with '*' (case-insensitive)."""

import copy
import re

from entities import InputGuardrailRequest, MutateGuardrailResponse

_WORDS = ("poison", "bomb")


def _redact(text: str) -> tuple[str, bool]:
    out = text
    changed = False
    for w in _WORDS:
        pattern = re.compile(re.escape(w), re.IGNORECASE)
        new_out, n = pattern.subn("*", out)
        if n:
            changed = True
            out = new_out
    return out, changed


def req_mutate(request: InputGuardrailRequest) -> MutateGuardrailResponse:
    body = copy.deepcopy(request.requestBody or {})
    any_change = False
    for msg in body.get("messages", []):
        content = msg.get("content")
        if isinstance(content, str):
            new_content, ch = _redact(content)
            if ch:
                msg["content"] = new_content
                any_change = True
    return MutateGuardrailResponse(verdict=True, transformed=any_change, result=body)
