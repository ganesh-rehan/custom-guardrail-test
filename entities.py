from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class ValidateGuardrailResponse(BaseModel):
    """Response body for validate-operation guardrails (AI Gateway JSON contract)."""

    verdict: bool
    message: Optional[str] = None


class MutateGuardrailResponse(BaseModel):
    """Response body for mutate-operation guardrails (AI Gateway JSON contract)."""

    verdict: bool
    transformed: bool
    result: dict[str, Any]


class SubjectType(str, Enum):
    user = 'user'
    team = 'team'
    serviceaccount = 'serviceaccount'


class Subject(BaseModel):
    subjectId: str
    subjectType: SubjectType
    subjectSlug: Optional[str] = None
    subjectDisplayName: Optional[str] = None


class RequestContext(BaseModel):
    user: Subject
    metadata: Optional[dict[str, str]] = None


class InputGuardrailRequest(BaseModel):
    requestBody: dict
    context: RequestContext
    config: Optional[dict] = None


class OutputGuardrailRequest(BaseModel):
    requestBody: dict
    responseBody: dict
    config: Optional[dict] = None
    context: RequestContext