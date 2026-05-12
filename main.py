from fastapi import FastAPI

from entities import InputGuardrailRequest, OutputGuardrailRequest
from guardrail.keyword_block import keyword_block
from guardrail.poison_tail_mutate import poison_tail_mutate
from guardrail.req_mutate import req_mutate
from guardrail.req_validate import req_validate
from guardrail.response_mutate import response_mutate
from guardrail.response_validate import response_validate

app = FastAPI(
    title="Custom Guardrail Server",
    description="Custom guardrails for TrueFoundry AI Gateway",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/keyword-block")
def keyword_block_endpoint(request: InputGuardrailRequest):
    return keyword_block(request)


@app.post("/poison-tail-mutate")
def poison_tail_mutate_endpoint(request: InputGuardrailRequest):
    return poison_tail_mutate(request)


@app.post("/req_validate")
def req_validate_endpoint(request: InputGuardrailRequest):
    """Input validate — block if message contains poison or bomb."""
    return req_validate(request)


@app.post("/req_mutate")
def req_mutate_endpoint(request: InputGuardrailRequest):
    """Input mutate — replace poison/bomb with * in request messages."""
    return req_mutate(request)


@app.post("/response_validate")
def response_validate_endpoint(request: OutputGuardrailRequest):
    """Output validate — block if assistant text contains poison or bomb."""
    return response_validate(request)


@app.post("/response_mutate")
def response_mutate_endpoint(request: OutputGuardrailRequest):
    """Output mutate — replace poison/bomb with * in assistant choices."""
    return response_mutate(request)
