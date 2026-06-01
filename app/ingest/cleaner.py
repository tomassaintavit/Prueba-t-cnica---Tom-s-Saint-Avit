import re


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def normalize_line_endings(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text
