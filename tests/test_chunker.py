import pytest

from app.ingest.chunker import chunk_text


def test_chunker_single_chunk():
    text = "Hola mundo"
    chunks = chunk_text(text, chunk_size=100, overlap=0)
    assert len(chunks) == 1
    assert chunks[0] == "Hola mundo"


def test_chunker_multiple_chunks():
    text = "A" * 2500
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    assert len(chunks) == 3
    assert all(len(c) <= 1000 for c in chunks)


def test_chunker_overlap_content():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chunks = chunk_text(text, chunk_size=10, overlap=5)
    assert len(chunks) >= 2
    if len(chunks) >= 2:
        assert chunks[1].startswith("FGHIJ")


def test_chunker_raises_for_zero_chunk_size():
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        chunk_text("test", chunk_size=0, overlap=0)


def test_chunker_raises_for_negative_overlap():
    with pytest.raises(ValueError, match="overlap must be non-negative"):
        chunk_text("test", chunk_size=10, overlap=-1)


def test_chunker_raises_for_overlap_equals_chunk_size():
    with pytest.raises(ValueError, match="overlap must be non-negative"):
        chunk_text("test", chunk_size=10, overlap=10)
