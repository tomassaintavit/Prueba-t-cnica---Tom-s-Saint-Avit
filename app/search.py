from __future__ import annotations

import logging
import os

from app.embeddings.embedder import Embedder
from app.llm import get_llm
from app.vector_store.chroma_store import VectorStore

logger = logging.getLogger(__name__)

REWRITE_PROMPT = """Extrae las 2 o 3 palabras clave de esta pregunta de soporte. Corrige errores ortográficos y reemplaza sinónimos informales por términos técnicos. Responde solo con las palabras separadas por espacios, sin puntuación ni explicaciones.

Ejemplos:
- ¿Cómo reinicio el servicio de autenticación? → autenticación credenciales
- El sistema devuelve error 502 → error conexión servidor
- No puedo acceder al dashboard → acceso sistema dashboard

Original: {question}
Palabras clave:"""

SYSTEM_PROMPT = """Eres un asistente que responde preguntas de soporte técnico. Responde únicamente con la respuesta directa, sin introducciones ni explicaciones sobre cómo respondes.

Reglas:
1. Máximo 150 palabras, en viñetas.
2. Después de cada viñeta, cita la fuente entre corchetes, ej. [1], [2].
3. Si el contexto no respalda una afirmación, escribe "Información insuficiente".
4. Si hay contradicciones, indica la contradicción y cita fuentes.
5. Lenguaje formal y conciso.
6. Si no hay contexto: 'No encontré información sobre esto en la documentación disponible.'"""


def _rewrite_question(question: str, llm) -> str:
    try:
        rewritten = llm.generate("Eres un asistente que reformula preguntas.", REWRITE_PROMPT.format(question=question))
        return rewritten.strip().strip('"').strip("'") or question
    except Exception:
        return question


def answer_question(question: str) -> str:
    threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
    top_k = int(os.getenv("TOP_K_RESULTS", "5"))
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    collection = os.getenv("COLLECTION_NAME", "support_docs")

    try:
        embedder = Embedder()
        store = VectorStore(db_path, collection)
        llm = get_llm()
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        return "Error interno del sistema. No se pudo inicializar el asistente."

    # rewritten = _rewrite_question(question, llm)
    # logger.info(f"Original: {question} → Rewritten: {rewritten}")
    # query_embedding = embedder.encode(rewritten)
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

    sources = sorted(set(r.get("source", "desconocido") for r in valid_results))

    try:
        answer = llm.generate(SYSTEM_PROMPT, user_prompt)
        if sources:
            answer += f"\n\n*Fuentes: {', '.join(sources)}*"
        return answer
    except Exception as e:
        logger.error(f"Error en LLM: {e}")
        return "Error al generar la respuesta. Intente nuevamente."
