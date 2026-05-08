from typing import Any, Dict, List
from entities import InputGuardrailRequest

# Default blocked keywords — can be overridden via config
DEFAULT_BLOCKED_KEYWORDS = ["bomb", "gun", "poison"]


def keyword_block(request: InputGuardrailRequest) -> Dict[str, Any]:
    """
    Input guardrail that checks whether user messages contain blocked keywords.

    IMPORTANT:
    - Policy outcomes are returned as HTTP 200 with structured verdict.
    - Do NOT raise HTTP 4xx for policy deny, otherwise gateway may classify it
      as execution error in `enforce_but_ignore_on_error`.
    """
    blocked_keywords: List[str] = (
        request.config.get("blocked_keywords", DEFAULT_BLOCKED_KEYWORDS)
        if request.config
        else DEFAULT_BLOCKED_KEYWORDS
    )

    messages = request.requestBody.get("messages", []) if request.requestBody else []

    for message in messages:
        content = message.get("content", "")
        if not isinstance(content, str):
            continue

        content_lower = content.lower()
        for keyword in blocked_keywords:
            if keyword.lower() in content_lower:
                # Policy deny -> return structured verdict (HTTP 200)
                return {
                    "result": False,   # backward-compatible signal
                    "verdict": False,  # explicit signal
                    "message": f"Request blocked: message contains a prohibited keyword '{keyword}'.",
                    "details": {
                        "matched_keyword": keyword,
                        "blocked_keywords": blocked_keywords,
                    },
                }

    # Policy pass -> return structured verdict (HTTP 200)
    return {
        "result": True,
        "verdict": True,
        "message": "No prohibited keywords found.",
        "details": {
            "blocked_keywords": blocked_keywords,
        },
    }