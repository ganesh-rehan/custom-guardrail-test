from typing import Optional
from fastapi import HTTPException
from entities import InputGuardrailRequest

# Default blocked keywords — can be overridden via config
DEFAULT_BLOCKED_KEYWORDS = ["bomb", "gun", "poison"]


def keyword_block(request: InputGuardrailRequest) -> Optional[dict]:
    """
    Input guardrail that blocks any message containing
    dangerous keywords: bomb, gun, poison.
    Keywords can be overridden via the 'blocked_keywords' config field.
    """
    blocked_keywords = (
        request.config.get("blocked_keywords", DEFAULT_BLOCKED_KEYWORDS)
        if request.config
        else DEFAULT_BLOCKED_KEYWORDS
    )

    messages = request.requestBody.get("messages", [])

    for message in messages:
        content = message.get("content", "")
        if not isinstance(content, str):
            continue

        content_lower = content.lower()
        for keyword in blocked_keywords:
            if keyword.lower() in content_lower:
                raise HTTPException(
                    status_code=400,
                    detail=f"Request blocked: message contains a prohibited keyword '{keyword}'."
                )

    # No blocked keywords found — allow the request
    return None