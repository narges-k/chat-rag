"""FastAPI app: a small chat UI backed by RagEngine."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.rag import RagEngine

app = FastAPI(title="docu-chat")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

_engine: RagEngine | None = None


def get_engine() -> RagEngine:
    global _engine
    if _engine is None:
        _engine = RagEngine()
    return _engine


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/")
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = get_engine().answer(req.question)
    return ChatResponse(**result)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
