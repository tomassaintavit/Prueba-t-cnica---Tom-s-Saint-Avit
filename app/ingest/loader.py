from abc import ABC, abstractmethod
from pathlib import Path


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, file_path: str | Path) -> str:
        ...


class TXTLoader(DocumentLoader):
    def load(self, file_path: str | Path) -> str:
        path = Path(file_path)
        return path.read_text(encoding="utf-8")


def get_loader(file_path: str | Path) -> DocumentLoader:
    ext = Path(file_path).suffix.lower()
    loaders = {
        ".txt": TXTLoader,
        ".md": TXTLoader,
    }
    loader_cls = loaders.get(ext)
    if loader_cls is None:
        raise ValueError(f"Unsupported file extension: {ext}")
    return loader_cls()
