from app.ingest import chunk_text


def test_chunk_text_keeps_short_text_as_one_chunk():
    text = "Just one short paragraph."
    chunks = chunk_text(text, chunk_size=800)
    assert chunks == [text]


def test_chunk_text_splits_on_paragraph_boundaries():
    text = ("A" * 500) + "\n\n" + ("B" * 500)
    chunks = chunk_text(text, chunk_size=600)
    assert len(chunks) == 2
    assert chunks[0].startswith("A")
    assert chunks[1].startswith("B")


def test_chunk_text_hard_splits_a_single_long_paragraph():
    text = "C" * 2000
    chunks = chunk_text(text, chunk_size=800, overlap=100)
    assert len(chunks) > 1
    # Every char of the original text should still appear somewhere.
    assert "".join(chunks).count("C") >= 2000
