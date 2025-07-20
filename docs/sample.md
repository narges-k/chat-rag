# About this project

docu-chat is a small retrieval-augmented generation (RAG) service. It indexes
the markdown and text files in this `docs/` folder into a local vector
database (Chroma) and answers questions about them using Claude.

## How retrieval works

1. Documents are split into overlapping chunks (~800 characters).
2. Each chunk is embedded and stored in Chroma.
3. When a question comes in, the most similar chunks are retrieved.
4. Those chunks are passed to Claude as context, and Claude answers using
   only that context.

## Replacing the sample docs

Delete this file and drop your own markdown or text files into `docs/`, then
run `python -m app.ingest` again to rebuild the index.
