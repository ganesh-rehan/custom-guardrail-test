from fastapi import FastAPI
from entities import InputGuardrailRequest
from guardrail.keyword_block import keyword_block

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
    Input guardrail: blocks requests containing 'bomb', 'gun', or 'poison'.
    Returns null (None → 200 with null body) if safe, raises HTTP 400 if blocked.
    """
    result = keyword_block(request)
    return result