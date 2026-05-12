"""Request (input) validate: deny if any user message contains 'poison' or 'bomb' (case-insensitive)."""

from entities import InputGuardrailRequest, ValidateGuardrailResponse

_FORBIDDEN = ("poison", "bomb")


def _contains_forbidden(text: str) -> bool:
    low = text.lower()
    return any(w in low for w in _FORBIDDEN)


def req_validate(request: InputGuardrailRequest) -> ValidateGuardrailResponse:
    for msg in request.requestBody.get("messages", []):
        content = msg.get("content")
        if isinstance(content, str) and _contains_forbidden(content):
            return ValidateGuardrailResponse(
                verdict=False,
                message="Request blocked: message contains 'poison' or 'bomb'.",
            )
    return ValidateGuardrailResponse(verdict=True)
