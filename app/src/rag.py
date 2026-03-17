
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def load_docs():
    docs = {}
    for path in DOCS_DIR.glob("*.md"):
        docs[path.stem] = path.read_text(encoding="utf-8")
    return docs


def retrieve(query: str, top_k: int = 5) -> list[tuple[str, str]]:
    docs = load_docs()
    items = list(docs.items())
    if len(items) <= top_k:
        return items
    return items[:top_k]
