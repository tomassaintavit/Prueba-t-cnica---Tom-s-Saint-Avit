"""
Evaluación del sistema RAG.

Métricas calculadas:
  Faithfulness       → qué tan factual es la respuesta dado el contexto (LLM judge)
  Context Relevance  → qué tan relevante es el contexto recuperado (LLM judge)
  Answer Relevance   → qué tan relevante es la respuesta a la pregunta (LLM judge)
  MRR @5             → Mean Reciprocal Rank de la recuperación
  Latencia promedio  → tiempo por consulta

Uso:
  source venv/bin/activate
  python scripts/eval_ragas.py
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from openai import OpenAI

from app.search import answer_question
from app.embeddings.embedder import Embedder
from app.vector_store.chroma_store import VectorStore


def _get_judge_client() -> tuple[OpenAI, str]:
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "groq":
        return (
            OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"),
            os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )
    if provider == "openai":
        return (
            OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
            "gpt-4o-mini",
        )
    # ollama (local)
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    return (
        OpenAI(api_key="ollama", base_url=f"{base_url}/v1"),
        os.getenv("OLLAMA_MODEL", "llama3.2"),
    )


CLIENT, JUDGE_MODEL = _get_judge_client()


def judge(prompt: str) -> float:
    """Pide al LLM juez un puntaje 0-5 y lo normaliza a 0-1."""
    response = CLIENT.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = response.choices[0].message.content.strip()

    # Extraer el primer número encontrado
    import re
    match = re.search(r"[\d.]+", text)
    score = float(match.group()) if match else 0.0

    # Normalizar de 0-5 a 0-1
    return min(score / 5.0, 1.0)


# ── Prompts para cada métrica ──────────────────────────────────────────

FAITHFULNESS_PROMPT = """
Evalúa del 0 al 5 qué tan fiel es la respuesta al contexto proporcionado.
0 = inventa información que no está en el contexto
5 = usa únicamente información del contexto, sin añadir nada externo

Contexto:
{context}

Respuesta:
{answer}

Puntaje (solo el número):
"""

CONTEXT_RELEVANCE_PROMPT = """
Evalúa del 0 al 5 qué tan relevante es el contexto para responder la pregunta.
0 = el contexto no tiene nada que ver con la pregunta
5 = el contexto contiene exactamente la información necesaria

Pregunta:
{question}

Contexto:
{context}

Puntaje (solo el número):
"""

ANSWER_RELEVANCE_PROMPT = """
Evalúa del 0 al 5 qué tan relevante es la respuesta a la pregunta.
0 = la respuesta no responde la pregunta en absoluto
5 = la respuesta responde completa y directamente

Pregunta:
{question}

Respuesta:
{answer}

Puntaje (solo el número):
"""


# ── Dataset de prueba ──────────────────────────────────────────────────
TEST_CASES = [
    {
        "question": "¿Qué hago si me aparece 'Usuario o contraseña incorrectos'?",
        "expected_contexts": ["Documentación 3.md"],
    },
    {
        "question": "El catálogo carga muy lento, ¿qué puedo hacer?",
        "expected_contexts": ["Documentación 1.pdf"],
    },
    {
        "question": "No se guardan los cambios de un material, ¿qué puede ser?",
        "expected_contexts": ["Documentación 1.pdf"],
    },
    {
        "question": "Me sale error de conexión con la base de datos, ¿qué hago?",
        "expected_contexts": ["Documentación 2.txt"],
    },
    {
        "question": "¿Cómo reinicio el servicio de autenticación?",
        "expected_contexts": [],
    },
]


# ── Evaluación ─────────────────────────────────────────────────────────
def run_evaluation():
    print("=" * 60)
    print("EVALUACIÓN DEL SISTEMA RAG")
    print("=" * 60)

    embedder = Embedder()
    store = VectorStore()
    results = []

    for i, tc in enumerate(TEST_CASES, 1):
        q = tc["question"]
        expected_sources = tc["expected_contexts"]

        print(f"\n[{i}/{len(TEST_CASES)}] {q}")
        print("-" * 60)

        # ── Búsqueda ────────────────────────────────────────────────
        t0 = time.time()
        q_emb = embedder.encode(q)
        search_results = store.search(q_emb, top_k=5)
        latency = time.time() - t0

        threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
        valid = [r for r in search_results if r["score"] >= threshold]

        retrieved_sources = list(set(r.get("source", "?") for r in valid))
        retrieved_texts = [r["text"] for r in valid]
        context_str = "\n\n".join(retrieved_texts) if retrieved_texts else "(sin contexto)"

        # ── MRR @5 ──────────────────────────────────────────────────
        import unicodedata

        def normalize(s: str) -> str:
            return unicodedata.normalize("NFC", s).lower()

        mrr = 0.0
        expected_norm = [normalize(e) for e in expected_sources]
        for rank, r in enumerate(search_results[:5], 1):
            src_norm = normalize(r.get("source", ""))
            if any(exp in src_norm for exp in expected_norm):
                mrr = 1.0 / rank
                break

        # ── Respuesta ───────────────────────────────────────────────
        t0 = time.time()
        answer = answer_question(q)
        total_latency = time.time() - t0

        # ── Faithfulness ────────────────────────────────────────────
        faithfulness = judge(
            FAITHFULNESS_PROMPT.format(context=context_str[:2000], answer=answer)
        )
        print(f"  Faithfulness:       {faithfulness:.3f}")

        # ── Context Relevance ───────────────────────────────────────
        context_relevance = judge(
            CONTEXT_RELEVANCE_PROMPT.format(question=q, context=context_str[:2000])
        )
        print(f"  Context Relevance:  {context_relevance:.3f}")

        # ── Answer Relevance ────────────────────────────────────────
        answer_relevance = judge(
            ANSWER_RELEVANCE_PROMPT.format(question=q, answer=answer)
        )
        print(f"  Answer Relevance:   {answer_relevance:.3f}")

        # ── Otras métricas ──────────────────────────────────────────
        print(f"  MRR @5:             {mrr:.3f}")
        print(f"  Retrieval latency:  {latency:.2f}s")
        print(f"  Total latency:      {total_latency:.2f}s")
        print(f"  Fuentes recuperadas: {', '.join(retrieved_sources) or '(ninguna)'}")
        print(f"  Respuesta: {answer[:150]}...")

        results.append({
            "question": q,
            "faithfulness": round(faithfulness, 3),
            "context_relevance": round(context_relevance, 3),
            "answer_relevance": round(answer_relevance, 3),
            "mrr_at_5": round(mrr, 3),
            "retrieval_latency": round(latency, 2),
            "total_latency": round(total_latency, 2),
            "retrieved_sources": retrieved_sources,
            "answer": answer,
        })

    # ── Resumen ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("RESUMEN GLOBAL")
    print("=" * 60)

    avg = {k: sum(r[k] for r in results) / len(results)
           for k in ["faithfulness", "context_relevance", "answer_relevance", "mrr_at_5"]}

    avg_latency = sum(r["total_latency"] for r in results) / len(results)
    avg_retrieval = sum(r["retrieval_latency"] for r in results) / len(results)

    print(f"  Faithfulness (avg):       {avg['faithfulness']:.3f}")
    print(f"  Context Relevance (avg):  {avg['context_relevance']:.3f}")
    print(f"  Answer Relevance (avg):   {avg['answer_relevance']:.3f}")
    print(f"  MRR @5 (avg):             {avg['mrr_at_5']:.3f}")
    print(f"  Latencia promedio:        {avg_latency:.2f}s")
    print(f"  Retrieval avg:            {avg_retrieval:.2f}s")

    # ── Guardar ─────────────────────────────────────────────────────
    output = {
        "metrics": {k: round(v, 3) for k, v in avg.items()},
        "avg_latency": round(avg_latency, 2),
        "avg_retrieval_latency": round(avg_retrieval, 2),
        "per_question": results,
    }
    out_path = Path(__file__).resolve().parent.parent / "eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n📁 Resultados guardados en {out_path}")


if __name__ == "__main__":
    run_evaluation()
