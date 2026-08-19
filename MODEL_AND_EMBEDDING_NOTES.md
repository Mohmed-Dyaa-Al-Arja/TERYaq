# Teryaq Backend / Model Update

## What is retained from the 3-day notebook

- Chunk size: 1000
- Chunk overlap: 200
- Top-K: 5
- Retrieval threshold: 0.65
- LLM: `qwen/qwen3.6-27b`
- Temperature: 0.1
- Max tokens: 700
- Groq OpenAI-compatible endpoint
- JSON output
- Reasoning effort: none
- Citation validation
- Claim-support validation
- Evidence-only grounded prompt

## Important embedding inconsistency in the notebook

The actual embedding code cell instantiated:

`sentence-transformers/all-MiniLM-L6-v2`

The final printed configuration text later says:

`BAAI/bge-small-en-v1.5`

These are not the same model.

For production parity with the evaluated vector store, this update uses:

`sentence-transformers/all-MiniLM-L6-v2`

Do NOT switch to BGE without rerunning the retrieval evaluation and threshold calibration.

## Do we need a second embedding model?

No.

Use one embedding model for the medical vector index.

The Qwen model is the generation / multimodal model. It is not an additional embedding model.

If BGE is tested later, replace the embedding model and rebuild/evaluate the index; do not mix two embedding models in the same collection.

## Old vehicle model layer

The old `models/qwen` package contained:

- vehicle prompt
- vehicle schema
- vehicle demo
- vehicle-oriented comments
- Hugging Face-oriented exception wording

Those concepts are removed from the new backend LLM layer.

The replacement is:

`backend/llm/`

with:

- `config.py`
- `client.py`
- `prompts.py`
- `schemas.py`
- `exceptions.py`
- `image_utils.py`

## Safety

Input safety is checked before retrieval.

Then retrieval must pass the evidence threshold.

Then generation happens only with accepted evidence.

Finally citations and claim support are validated. Failure is fail-closed.
