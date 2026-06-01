from app.ingest.cleaner import clean_text, normalize_line_endings


def test_clean_text_collapses_whitespace():
    result = clean_text("Hola    mundo\nesto   es  una prueba")
    assert result == "Hola mundo esto es una prueba"


def test_clean_text_strips_edges():
    result = clean_text("  hola mundo  ")
    assert result == "hola mundo"


def test_clean_text_empty():
    assert clean_text("") == ""
    assert clean_text("   ") == ""


def test_normalize_line_endings_crlf():
    result = normalize_line_endings("linea1\r\nlinea2\r\nlinea3")
    assert result == "linea1\nlinea2\nlinea3"


def test_normalize_line_endings_cr():
    result = normalize_line_endings("linea1\rlinea2\rlinea3")
    assert result == "linea1\nlinea2\nlinea3"


def test_normalize_line_endings_mixed():
    result = normalize_line_endings("linea1\r\nlinea2\rlinea3\nlinea4")
    assert result == "linea1\nlinea2\nlinea3\nlinea4"
