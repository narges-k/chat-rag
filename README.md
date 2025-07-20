# docu-chat

A small retrieval-augmented generation (RAG) service: it indexes your own
markdown/text docs into a local vector database and answers questions about
them using Claude, with sources cited.

```
docs/*.md ──► chunk ──► Chroma (local vector DB) ──► top-k retrieval
                                                          │
question ───────────────────────────────────────────────►│
                                                          ▼
                                              Claude (Anthropic API)
                                                          │
                                                          ▼
                                              answer + cited sources
```

## Why this exists

Most RAG demos hardcode a single script. This one is split into a proper
ingestion step, a retrieval/generation module, and a thin API + UI on top —
closer to how you'd structure something meant to actually run somewhere.

## Quickstart

```bash
git clone <this-repo>
cd docu-chat
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env          # then add your ANTHROPIC_API_KEY

# put your own .md / .txt files in docs/ (a sample is included)
python -m app.ingest           # builds the local vector index

uvicorn app.main:app --reload  # open http://localhost:8000
```

## Or with Docker

```bash
cp .env.example .env   # add your ANTHROPIC_API_KEY
docker compose up --build
```

## Running the tests

```bash
pytest -q
```

Tests mock the Anthropic API call, so they run without a key or network
access — only `app/ingest.py`'s chunking logic and `app/rag.py`'s prompt
construction are under test, plus a check that `answer()` wires the pieces
together correctly.

## Project layout

```
app/
  config.py    settings (env vars via pydantic-settings)
  ingest.py    load docs → chunk → upsert into Chroma
  rag.py       retrieve chunks → build prompt → call Claude
  main.py      FastAPI routes (/chat, /health) + static chat UI
docs/          the documents that get indexed
tests/         pytest unit tests
```

## Known limitations / next steps

- Chunking is paragraph-based, not semantic — fine for docs, not for code.
- No auth on the API; add one before exposing this beyond localhost.
- Only markdown/txt are ingested; `pypdf` is in requirements for adding PDF
  support next.

## License

MIT — see [LICENSE](LICENSE).
