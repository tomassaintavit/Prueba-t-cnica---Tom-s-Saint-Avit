from __future__ import annotations

import uuid
from pathlib import Path

from app.embeddings.embedder import Embedder
from app.ingest.cleaner import clean_text, normalize_line_endings
from app.ingest.chunker import chunk_text
from app.ingest.loader import get_loader
from app.vector_store.chroma_store import VectorStore


def run_ingest_pipeline(
    docs_dir: str | Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    embedding_model: str = "all-MiniLM-L6-v2",
    db_path: str | Path = "./chroma_db",
    collection_name: str = "support_docs",
) -> int:
    embedder = Embedder(embedding_model)
    store = VectorStore(db_path, collection_name)
    docs_dir = Path(docs_dir)

    total_chunks = 0
    files = sorted(docs_dir.iterdir())

    for file_path in files:
        if file_path.suffix.lower() not in {".txt", ".md", ".json", ".pdf"}:
            continue

        loader = get_loader(str(file_path))
        raw_text = loader.load(str(file_path))
        text = normalize_line_endings(raw_text)
        text = clean_text(text)
        chunks = chunk_text(text, chunk_size, chunk_overlap)

        source = file_path.name
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source": source} for _ in chunks]
        embeddings = embedder.encode_batch(chunks)
        store.index(ids, chunks, embeddings, metadatas)
        total_chunks += len(chunks)

    return total_chunks
