from fastapi import FastAPI
from entities import InputGuardrailRequest
from guardrail.keyword_block import keyword_block
from guardrail.poison_tail_mutate import poison_tail_mutate  # NEW

app = FastAPI(
    title="Custom Guardrail Server",
    description="Keyword-based input guardrail for TrueFoundry AI Gateway",
    version="1.0.0"
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


@app.post("/poison-tail-mutate")  # NEW
def poison_tail_mutate_endpoint(request: InputGuardrailRequest):
    """
    Mutate guardrail endpoint.
    Masks everything after the word 'poison' in user message content.
    Returns structured mutate response (HTTP 200).
    """
    return poison_tail_mutate(request)