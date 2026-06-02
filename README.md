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
cd <carpeta donde va a estar el sistema>

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Descargar modelo de Ollama (si usas LLM local)
ollama pull llama3.2

# Ejecutar ingesta de documentos
python scripts/ingest_all.py

# Iniciar API
python scripts/run_api.py
```

## Uso — API directa

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "No puedo acceder al dashboard"}'
```

## Uso — n8n

1. Inicia n8n: `n8n start`
2. Abre `http://localhost:5678`
3. Importa el workflow: Workflows → Import → seleccionar `workflows/support_assistant.json`
4. Activa el workflow con el toggle superior derecho
5. Envía preguntas al webhook:

```bash
curl -X POST "http://localhost:5678/webhook/support-query" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cómo reinicio el servicio de autenticación?"}'
```

> **Nota:** Si el workflow no está activo, usa la URL de prueba:
> `http://localhost:5678/webhook-test/support-query`

## Uso — Frontend Streamlit

```bash
# En otra terminal, con el venv activo y la API corriendo:
streamlit run streamlit_app.py
```

Abre `http://localhost:8501` en el navegador.

## Estructura

```
├── app/           # Código fuente Python
│   ├── ingest/    # Carga, limpieza y chunking de documentos
│   ├── embeddings/ # Generación de vectores (Sentence Transformers)
│   ├── vector_store/ # ChromaDB (indexación y búsqueda)
│   ├── llm/       # Abstracción de LLM (OpenAI + Ollama)
│   └── api/       # FastAPI endpoints
├── docs/          # Documentación técnica (input del RAG)
├── workflows/     # Workflows exportados de n8n
└── scripts/       # Scripts de utilidad
```
