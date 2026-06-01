"""
Script de ingesta de documentos.
Procesa todos los archivos en docs/ y los indexa en ChromaDB.

Uso: python scripts/ingest_all.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if __name__ == "__main__":
    print("Ingesta de documentos — próximamente")
