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
    Mutate request body when used as input guardrail.
    Mutate response body when used as output guardrail.

    Rule:
    - If text contains keyword (default: 'poison'), mask everything after it with '*'.
    """
    keyword = (request.config or {}).get("keyword", DEFAULT_KEYWORD)
    mask_char = (request.config or {}).get("mask_char", DEFAULT_MASK_CHAR)

    # Detect whether this is output-guardrail payload
    raw_response_body = getattr(request, "responseBody", None)
    is_output_guardrail = raw_response_body is not None

    if is_output_guardrail:
        target_body: Dict[str, Any] = deepcopy(raw_response_body or {})
        target_label = "responseBody"

        # OpenAI-style response content location
        # response.choices[i].message.content
        choices = target_body.get("choices", [])
        mutated = False
        mutated_choice_indices: List[int] = []

        for i, choice in enumerate(choices):
            message = choice.get("message", {}) if isinstance(choice, dict) else {}
            content = message.get("content")

            if isinstance(content, str):
                new_content, changed = _mask_after_keyword(content, keyword, mask_char)
                if changed:
                    message["content"] = new_content
                    choice["message"] = message
                    mutated = True
                    mutated_choice_indices.append(i)
                continue

            # Optional multimodal response support
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
                    message["content"] = content
                    choice["message"] = message
                    mutated = True
                    mutated_choice_indices.append(i)

        target_body["choices"] = choices

        return {
            "verdict": True,
            "transformed": mutated,
            "result": target_body,
            "message": "Poison tail masked in response" if mutated else "No poison keyword found in response",
            "details": {
                "keyword": keyword,
                "mutated": mutated,
                "target": target_label,
                "mutated_choice_indices": mutated_choice_indices,
            },
        }

    # Input guardrail path -> mutate requestBody
    target_body = deepcopy(request.requestBody or {})
    target_label = "requestBody"

    messages: List[Dict[str, Any]] = target_body.get("messages", [])
    mutated = False
    mutated_message_indices: List[int] = []

    for i, msg in enumerate(messages):
        if msg.get("role") != "user":
            continue

        content = msg.get("content")

        if isinstance(content, str):
            new_content, changed = _mask_after_keyword(content, keyword, mask_char)
            if changed:
                msg["content"] = new_content
                mutated = True
                mutated_message_indices.append(i)
            continue

        # Optional multimodal user content support
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
                msg["content"] = content
                mutated = True
                mutated_message_indices.append(i)

    target_body["messages"] = messages

    return {
        "verdict": True,
        "transformed": mutated,
        "result": target_body,
        "message": "Poison tail masked in request" if mutated else "No poison keyword found in request",
        "details": {
            "keyword": keyword,
            "mutated": mutated,
            "target": target_label,
            "mutated_message_indices": mutated_message_indices,
        },
    }