from fastapi import FastAPI

from entities import InputGuardrailRequest, OutputGuardrailRequest
from guardrail.drug_mention_guardrails_ai import drug_mention
from guardrail.keyword_block import keyword_block
from guardrail.nsfw_filtering_local_eval import nsfw_filtering
from guardrail.pii_detection_guardrails_ai import pii_detection_guardrails_ai
from guardrail.pii_redaction_presidio import process_input_guardrail
from guardrail.poison_tail_mutate import poison_tail_mutate
from guardrail.web_sanitization_guardrails_ai import web_sanitization

app = FastAPI(
    title="Custom Guardrail Server",
    description="Keyword-based input guardrail for TrueFoundry AI Gateway",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/keyword-block")
def keyword_block_endpoint(request: InputGuardrailRequest):
    """
    Validate guardrail endpoint.
    Returns structured verdict (HTTP 200).
    """
    return keyword_block(request)


@app.post("/poison-tail-mutate")
def poison_tail_mutate_endpoint(request: InputGuardrailRequest):
    """
    Mutate guardrail endpoint.
    Masks everything after the word 'poison' in user message content.
    Returns structured mutate response (HTTP 200).
    """
    return poison_tail_mutate(request)


@app.post("/pii-redaction")
def pii_redaction_endpoint(request: InputGuardrailRequest):
    """Input mutate — Presidio PII redaction (requires `presidio_entities` + presidio deps)."""
    return process_input_guardrail(request)


@app.post("/nsfw-filtering")
def nsfw_filtering_endpoint(request: OutputGuardrailRequest):
    """Output validate — local NSFW classifier."""
    return nsfw_filtering(request)


@app.post("/drug-mention")
def drug_mention_endpoint(request: OutputGuardrailRequest):
    """Output validate — Guardrails AI drug mention."""
    return drug_mention(request)


@app.post("/web-sanitization")
def web_sanitization_endpoint(request: InputGuardrailRequest):
    """Input validate — Guardrails AI web sanitization."""
    return web_sanitization(request)


@app.post("/pii-detection")
def pii_detection_endpoint(request: InputGuardrailRequest):
    """Input validate — Guardrails AI PII detection."""
    return pii_detection_guardrails_ai(request)
