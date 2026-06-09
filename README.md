# Asistente de Soporte Automatizado — RAG con n8n + Python + LLM

Sistema RAG (Retrieval-Augmented Generation) que responde consultas de soporte
técnico usando documentación interna. Orquestado con n8n, procesado con Python,
y potenciado por LLMs locales (Ollama) o cloud (OpenAI/Groq).

## Stack

- **n8n** — Workflow y webhook
- **FastAPI** — API REST
- **ChromaDB** — Vector store local
- **Sentence Transformers** — Embeddings
- **OpenAI / Groq / Ollama** — LLM intercambiable

## Requisitos

- **n8n** (Community Edition)
- Ollama (opcional, para LLM local)
- API key de OpenAI o Groq (opcional, para LLM cloud)

## Instalación

### Opción 1: Native (Python)

```bash
# Clonar repositorio
git clone <repo-url>
cd <directorio>

# Crear entorno virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Descargar modelo de Ollama (si usas LLM local)
ollama pull llama3.2

# Indexar documentos en ChromaDB
python scripts/ingest_all.py

# Iniciar API
python scripts/run_api.py
```

### Opción 2: Docker

```bash
# Clonar repositorio
git clone <repo-url>
cd <directorio>

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Construir e iniciar
docker compose up --build
```

La API queda disponible en `http://localhost:8000`.

> Nota: n8n y Ollama se ejecutan fuera del contenedor.
> El workflow de n8n apunta a `http://127.0.0.1:8000/query` y funciona sin cambios.

## Uso

### API directa

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "No puedo acceder al dashboard"}'
```

### n8n

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

### Streamlit (frontend de prueba)

Con la API corriendo:

```bash
streamlit run streamlit_app.py
```

Abre `http://localhost:8501` en el navegador.

## Re-indexar documentos

Si agregás, modificás o borrás archivos en `docs/`, o cambiás el modelo de embedding en `.env`, necesitás re-indexar:

```bash
# Native
source venv/bin/activate
rm -rf chroma_db/
python scripts/ingest_all.py

# Docker
docker compose down
rm -rf chroma_db/
docker compose up --build
```

> `chroma_db/` está en `.gitignore`, no se commitea nunca.

## Estructura

```
├── app/           # Código fuente Python
│   ├── ingest/    # Carga, limpieza y chunking de documentos
│   ├── embeddings/ # Generación de vectores (Sentence Transformers)
│   ├── vector_store/ # ChromaDB (indexación y búsqueda)
│   ├── llm/       # Abstracción de LLM (OpenAI/Groq/Ollama)
│   └── api/       # FastAPI endpoints
├── docs/          # Documentación técnica (input del RAG)
├── workflows/     # Workflows exportados de n8n
├── scripts/       # Scripts de utilidad
├── Dockerfile
└── docker-compose.yml
```
