from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    category: str
    source: str
    content: str
    path: str


def _stable_id(path: Path, content: str) -> str:
    digest = hashlib.sha1(f"{path.name}:{content}".encode("utf-8")).hexdigest()
    return digest[:16]


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip().strip('"')
    return metadata, parts[2].strip()


def _document_from_json(path: Path) -> Document:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    content = str(data.get("content", "")).strip()
    title = str(data.get("title") or path.stem).strip()
    return Document(
        doc_id=str(data.get("doc_id") or _stable_id(path, content)),
        title=title,
        category=str(data.get("category") or "未分类").strip(),
        source=str(data.get("source") or path.name).strip(),
        content=content,
        path=str(path),
    )


def _document_from_text(path: Path) -> Document:
    raw_text = path.read_text(encoding="utf-8")
    metadata, content = _parse_front_matter(raw_text)
    title = metadata.get("title") or path.stem.replace("_", " ")
    category = metadata.get("category") or "未分类"
    source = metadata.get("source") or path.name
    return Document(
        doc_id=_stable_id(path, content),
        title=title.strip(),
        category=category.strip(),
        source=source.strip(),
        content=content.strip(),
        path=str(path),
    )


def load_documents(knowledge_base_dir: Path) -> list[Document]:
    if not knowledge_base_dir.exists():
        return []

    documents: list[Document] = []
    for path in sorted(knowledge_base_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".json"}:
            continue
        try:
            document = _document_from_json(path) if path.suffix.lower() == ".json" else _document_from_text(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Failed to load document {path.name}: {exc}") from exc
        if document.content:
            documents.append(document)
    return documents
