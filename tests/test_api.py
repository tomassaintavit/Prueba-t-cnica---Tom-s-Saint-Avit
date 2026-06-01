import pytest
from fastapi.testclient import TestClient

from app.api.routes import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_empty_question():
    response = client.post("/query", json={"question": "  "})
    assert response.status_code == 400
    assert "vacía" in response.json()["detail"]


def test_query_missing_field():
    response = client.post("/query", json={})
    assert response.status_code == 422


def test_query_valid_request(monkeypatch):
    def mock_answer(question: str) -> str:
        return "Respuesta de prueba"

    monkeypatch.setattr("app.api.routes.answer_question", mock_answer)

    response = client.post("/query", json={"question": "¿Cómo reinicio el servicio?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Respuesta de prueba"
