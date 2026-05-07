from enum import Enum
from typing import Optional
from pydantic import BaseModel


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