# Asistente de Soporte Automatizado — RAG con n8n + Python + LLM

Sistema RAG (Retrieval-Augmented Generation) que responde consultas de soporte
técnico usando documentación interna. Orquestado con n8n, procesado con Python,
y potenciado por LLMs locales (Ollama) o cloud (OpenAI).

## Stack

- **n8n** — Workflow y webhook
- **FastAPI** — API REST
- **ChromaDB** — Vector store local
- **Sentence Transformers** — Embeddings
- **OpenAI / Ollama** — LLM intercambiable

## Requisitos

- Python 3.9+
- n8n (Community Edition)
- Ollama (opcional, para LLM local)
- API key de OpenAI (opcional, para LLM cloud)

## Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd UNILINK

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar ingesta de documentos
python scripts/ingest_all.py

# Iniciar API
python scripts/run_api.py
```

## Uso

```bash
# Consultar desde CLI
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cómo reinicio el servicio de autenticación?"}'
```

## Estructura

```
├── app/           # Código fuente Python
├── agents/        # Contexto para asistentes IA
├── docs/          # Documentación técnica
├── workflows/     # Workflows n8n
├── scripts/       # Scripts de utilidad
└── chroma_db/     # Base de datos vectorial (generado)
```
