from unittest.mock import MagicMock

from app.rag import RagEngine


def make_engine_without_init():
    """Build a RagEngine instance while skipping the real __init__
    (which would open a Chroma DB and an Anthropic client)."""
    engine = RagEngine.__new__(RagEngine)
    return engine


def test_build_prompt_includes_numbered_sources():
    engine = make_engine_without_init()
    hits = [
        {"text": "Chunk one text", "source": "docs/a.md", "distance": 0.1},
        {"text": "Chunk two text", "source": "docs/b.md", "distance": 0.2},
    ]
    prompt = engine.build_prompt("What is X?", hits)
    assert "[1]" in prompt and "[2]" in prompt
    assert "docs/a.md" in prompt and "docs/b.md" in prompt
    assert "What is X?" in prompt


def test_build_prompt_handles_no_hits():
    engine = make_engine_without_init()
    prompt = engine.build_prompt("What is X?", [])
    assert "no context found" in prompt


def test_answer_calls_anthropic_and_returns_sources(mocker):
    engine = make_engine_without_init()
    engine.top_k = 4
    engine.retrieve = MagicMock(
        return_value=[{"text": "t", "source": "docs/a.md", "distance": 0.1}]
    )

    fake_block = MagicMock(type="text", text="The answer is 42.")
    fake_response = MagicMock(content=[fake_block])
    engine._anthropic = MagicMock()
    engine._anthropic.messages.create.return_value = fake_response

    result = engine.answer("What is the answer?")

    assert result["answer"] == "The answer is 42."
    assert result["sources"] == ["docs/a.md"]
    engine._anthropic.messages.create.assert_called_once()
