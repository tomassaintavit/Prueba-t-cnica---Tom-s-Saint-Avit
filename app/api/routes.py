from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.search import answer_question

app = FastAPI(title="Support Assistant RAG")


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    answer = answer_question(question)
    return QueryResponse(answer=answer)


@app.get("/health")
def health():
    return {"status": "ok"}
