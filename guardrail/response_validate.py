"""Response (output) validate: deny if assistant content contains 'poison' or 'bomb' (case-insensitive)."""

from entities import OutputGuardrailRequest, ValidateGuardrailResponse

_FORBIDDEN = ("poison", "bomb")


def _contains_forbidden(text: str) -> bool:
    low = text.lower()
    return any(w in low for w in _FORBIDDEN)


def response_validate(request: OutputGuardrailRequest) -> ValidateGuardrailResponse:
    for choice in request.responseBody.get("choices", []):
        message = choice.get("message", {})
        content = message.get("content")
        if isinstance(content, str) and _contains_forbidden(content):
            return ValidateGuardrailResponse(
                verdict=False,
                message="Response blocked: assistant content contains 'poison' or 'bomb'.",
            )
    return ValidateGuardrailResponse(verdict=True)
