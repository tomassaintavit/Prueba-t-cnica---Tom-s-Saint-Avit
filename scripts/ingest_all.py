"""
Ingesta todos los documentos en docs/ y los indexa en ChromaDB.

Uso: python scripts/ingest_all.py
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ingest.pipeline import run_ingest_pipeline


if __name__ == "__main__":
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    total = run_ingest_pipeline(docs_dir)
    print(f"Ingesta completada. {total} chunks indexados.")
