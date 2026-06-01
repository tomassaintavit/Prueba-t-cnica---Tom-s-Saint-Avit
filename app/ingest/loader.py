from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pypdf import PdfReader


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, file_path: str | Path) -> str:
        ...


class TXTLoader(DocumentLoader):
    def load(self, file_path: str | Path) -> str:
        path = Path(file_path)
        return path.read_text(encoding="utf-8")


class PDFLoader(DocumentLoader):
    def load(self, file_path: str | Path) -> str:
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)


class JSONLoader(DocumentLoader):
    def load(self, file_path: str | Path) -> str:
        path = Path(file_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return self._flatten(data)

    def _flatten(self, obj: Any, level: int = 0) -> str:
        indent = "  " * level
        parts = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (list, dict)):
                    nested = self._flatten(value, level + 1)
                    if nested.strip():
                        parts.append(f"{indent}{key}:")
                        parts.append(nested)
                else:
                    parts.append(f"{indent}{key}: {value}")
        elif isinstance(obj, list):
            for item in obj:
                nested = self._flatten(item, level + 1)
                if nested.strip():
                    parts.append(nested)
        elif isinstance(obj, str):
            parts.append(f"{indent}{obj}")

        return "\n".join(parts)


def get_loader(file_path: str | Path) -> DocumentLoader:
    ext = Path(file_path).suffix.lower()
    loaders: dict[str, type[DocumentLoader]] = {
        ".txt": TXTLoader,
        ".md": TXTLoader,
        ".json": JSONLoader,
        ".pdf": PDFLoader,
    }
    loader_cls = loaders.get(ext)
    if loader_cls is None:
        raise ValueError(f"Unsupported file extension: {ext}")
    return loader_cls()
