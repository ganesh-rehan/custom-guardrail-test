"""Response (output) mutate: replace 'poison' or 'bomb' in assistant messages with '*' (case-insensitive)."""

import copy
import re

from entities import OutputGuardrailRequest, MutateGuardrailResponse

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


def response_mutate(request: OutputGuardrailRequest) -> MutateGuardrailResponse:
    body = copy.deepcopy(request.responseBody or {})
    any_change = False
    for choice in body.get("choices", []):
        message = choice.get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            new_content, ch = _redact(content)
            if ch:
                message["content"] = new_content
                choice["message"] = message
                any_change = True
    return MutateGuardrailResponse(verdict=True, transformed=any_change, result=body)
