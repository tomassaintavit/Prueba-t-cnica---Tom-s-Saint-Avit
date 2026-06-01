from __future__ import annotations

import os

from app.embeddings.embedder import Embedder
from app.llm import get_llm
from app.vector_store.chroma_store import VectorStore

SYSTEM_PROMPT = """Eres un asistente que debe responder usando únicamente la información de los bloques CONTEXT anteriores.
1. Responde la pregunta en máximo 150 palabras usando viñetas.
2. Después de cada viñeta, incluye la cita de la fuente entre corchetes, ej. [1], [2].
3. Si el contexto no respalda una afirmación, escribe "Información insuficiente" en lugar de inventar.
4. Si varios contextos se contradicen, indica la contradicción y cita las fuentes.
5. Mantén un lenguaje formal y conciso.
6. Si no hay contexto, responde: 'No encontré información sobre esto en la documentación disponible.'"""


def answer_question(question: str) -> str:
    threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
    top_k = int(os.getenv("TOP_K_RESULTS", "5"))
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    collection = os.getenv("COLLECTION_NAME", "support_docs")

    embedder = Embedder()
    store = VectorStore(db_path, collection)
    llm = get_llm()

    query_embedding = embedder.encode(question)
    results = store.search(query_embedding, top_k)

    valid_results = [r for r in results if r["score"] >= threshold]

    if not valid_results:
        return "No encontré información sobre esto en la documentación disponible."

    context_blocks = []
    for i, r in enumerate(valid_results, 1):
        source = r.get("source", "desconocido")
        short_excerpt = r["text"][:100].replace("\n", " ")
        header = f"[CONTEXT {i}] [{i}] Title: {source} | {short_excerpt}..."
        context_blocks.append(f"{header}\n{r['text']}")

    context_str = "\n\n".join(context_blocks)
    user_prompt = f"{context_str}\n\nQUESTION: {question}"

    return llm.generate(SYSTEM_PROMPT, user_prompt)
