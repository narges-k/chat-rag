"""Load documents from disk, chunk them, and index them in Chroma.

Kept deliberately simple: markdown/text files are split on paragraph
boundaries into ~800 character chunks with a small overlap, which is enough
for a documentation-sized corpus without pulling in a heavy NLP dependency.
"""
from __future__ import annotations

import pathlib

import chromadb

from app.config import settings

SUPPORTED_SUFFIXES = {".md", ".txt"}


def load_documents(docs_dir: str | pathlib.Path) -> list[tuple[str, str]]:
    """Return a list of (source_path, raw_text) for every supported file."""
    docs_dir = pathlib.Path(docs_dir)
    documents: list[tuple[str, str]] = []
    for path in sorted(docs_dir.rglob("*")):
        if path.suffix.lower() in SUPPORTED_SUFFIXES and path.is_file():
            documents.append((str(path), path.read_text(encoding="utf-8")))
    return documents


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Split text into overlapping chunks, breaking on paragraphs where possible."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buffer = ""
    for para in paragraphs:
        if len(buffer) + len(para) + 1 <= chunk_size:
            buffer = f"{buffer}\n\n{para}".strip()
        else:
            if buffer:
                chunks.append(buffer)
            buffer = para
    if buffer:
        chunks.append(buffer)

    # Fallback: a single paragraph longer than chunk_size still needs splitting.
    final_chunks: list[str] = []
    for chunk in chunks:
        if len(chunk) <= chunk_size:
            final_chunks.append(chunk)
            continue
        start = 0
        while start < len(chunk):
            end = start + chunk_size
            final_chunks.append(chunk[start:end])
            start = end - overlap
    return final_chunks


def build_index(docs_dir: str | None = None, chroma_dir: str | None = None) -> int:
    """Ingest every document in docs_dir into a persistent Chroma collection.

    Returns the number of chunks indexed.
    """
    docs_dir = docs_dir or settings.docs_dir
    chroma_dir = chroma_dir or settings.chroma_dir

    client = chromadb.PersistentClient(path=chroma_dir)
    collection = client.get_or_create_collection("docs")

    ids, texts, metadatas = [], [], []
    for source, raw_text in load_documents(docs_dir):
        for i, chunk in enumerate(chunk_text(raw_text)):
            ids.append(f"{source}::{i}")
            texts.append(chunk)
            metadatas.append({"source": source, "chunk": i})

    if not texts:
        return 0

    # Chroma dedupes by id, so re-running ingest after editing docs is safe.
    collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
    return len(texts)


if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks from '{settings.docs_dir}' into '{settings.chroma_dir}'.")
