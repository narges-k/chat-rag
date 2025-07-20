"""Retrieval-augmented generation: fetch relevant chunks, ask Claude, cite sources."""
from __future__ import annotations

import anthropic
import chromadb

from app.config import settings

SYSTEM_PROMPT = (
    "You are a documentation assistant. Answer the user's question using ONLY the "
    "provided context. If the context does not contain the answer, say you don't "
    "know instead of guessing. Keep answers concise and cite sources by their "
    "[number] as given in the context."
)


class RagEngine:
    """Thin wrapper around a Chroma collection + the Anthropic Messages API."""

    def __init__(self, chroma_dir: str | None = None, top_k: int | None = None) -> None:
        self.chroma_dir = chroma_dir or settings.chroma_dir
        self.top_k = top_k or settings.top_k
        self._client = chromadb.PersistentClient(path=self.chroma_dir)
        self._collection = self._client.get_or_create_collection("docs")
        self._anthropic = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def retrieve(self, question: str) -> list[dict]:
        """Return the top-k most relevant chunks for the question."""
        if self._collection.count() == 0:
            return []
        result = self._collection.query(query_texts=[question], n_results=self.top_k)
        hits = []
        for doc, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            hits.append({"text": doc, "source": meta["source"], "distance": dist})
        return hits

    def build_prompt(self, question: str, hits: list[dict]) -> str:
        context_blocks = [
            f"[{i + 1}] (source: {h['source']})\n{h['text']}" for i, h in enumerate(hits)
        ]
        context = "\n\n".join(context_blocks) if context_blocks else "(no context found)"
        return f"Context:\n{context}\n\nQuestion: {question}"

    def answer(self, question: str) -> dict:
        """Retrieve context, call Claude, and return the answer plus its sources."""
        hits = self.retrieve(question)
        prompt = self.build_prompt(question, hits)

        response = self._anthropic.messages.create(
            model=settings.claude_model,
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return {
            "answer": text,
            "sources": sorted({h["source"] for h in hits}),
        }
