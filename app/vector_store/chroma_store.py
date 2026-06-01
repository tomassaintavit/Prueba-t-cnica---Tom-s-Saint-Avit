from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings


class VectorStore:
    def __init__(self, db_path: str | Path = "./chroma_db", collection_name: str = "support_docs"):
        self._client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def index(self, ids: list[str], texts: list[str], embeddings: list[list[float]]) -> None:
        self._collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
        )

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        return [
            {"id": id_, "text": doc, "score": 1 - dist}
            for id_, doc, dist in zip(ids, documents, distances)
        ]

    def count(self) -> int:
        return self._collection.count()
