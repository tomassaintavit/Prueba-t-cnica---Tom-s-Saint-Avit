import json
from pathlib import Path

import pytest

from app.ingest.loader import get_loader


def test_txt_loader(tmp_path: Path):
    file = tmp_path / "test.txt"
    file.write_text("Hola mundo", encoding="utf-8")
    loader = get_loader(str(file))
    assert loader.load(str(file)) == "Hola mundo"


def test_md_loader(tmp_path: Path):
    file = tmp_path / "test.md"
    file.write_text("# Titulo\n\nParrafo.", encoding="utf-8")
    loader = get_loader(str(file))
    assert "# Titulo\n\nParrafo." in loader.load(str(file))


def test_json_loader(tmp_path: Path):
    data = {"key": "valor", "lista": [1, 2]}
    file = tmp_path / "test.json"
    file.write_text(json.dumps(data), encoding="utf-8")
    loader = get_loader(str(file))
    result = loader.load(str(file))
    assert "key" in result
    assert "valor" in result


def test_json_loader_nested(tmp_path: Path):
    data = {
        "modulo": "errores",
        "contenido": [
            {"titulo": "Error 1", "solucion": "Reiniciar"},
        ],
    }
    file = tmp_path / "test.json"
    file.write_text(json.dumps(data), encoding="utf-8")
    loader = get_loader(str(file))
    result = loader.load(str(file))
    assert "Error 1" in result
    assert "Reiniciar" in result


def test_pdf_loader(tmp_path: Path):
    from pypdf import PdfWriter

    file = tmp_path / "test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(72, 72)
    writer.write(str(file))

    loader = get_loader(str(file))
    result = loader.load(str(file))
    assert isinstance(result, str)


def test_unsupported_extension(tmp_path: Path):
    file = tmp_path / "test.csv"
    file.write_text("a,b,c", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file extension"):
        get_loader(str(file))
