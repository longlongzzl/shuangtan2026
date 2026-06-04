from __future__ import annotations

import re
from dataclasses import asdict

from app.rag.document_loader import Document


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?；;])\s*")


def _split_text_units(text: str) -> list[str]:
    units: list[str] = []
    for paragraph_units in _split_paragraph_units(text):
        units.extend(paragraph_units)
    return units


def _split_paragraph_units(text: str) -> list[list[str]]:
    units: list[str] = []
    paragraphs: list[list[str]] = []
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        paragraph = re.sub(r"\s+", " ", paragraph).strip()
        if not paragraph:
            continue
        sentences = [item.strip() for item in _SENTENCE_SPLIT_RE.split(paragraph) if item.strip()]
        units = sentences or [paragraph]
        paragraphs.append(units)
    return paragraphs


class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80) -> None:
        self.chunk_size = max(120, chunk_size)
        self.chunk_overlap = max(0, min(chunk_overlap, self.chunk_size // 2))

    def chunk_documents(self, documents: list[Document]) -> list[dict]:
        chunks: list[dict] = []
        for document in documents:
            chunks.extend(self.chunk_document(document))
        return chunks

    def chunk_document(self, document: Document) -> list[dict]:
        paragraphs = _split_paragraph_units(document.content)
        chunks: list[dict] = []

        def emit(text: str) -> None:
            cleaned = text.strip()
            if not cleaned:
                return
            chunk_index = len(chunks)
            metadata = {
                "doc_id": document.doc_id,
                "title": document.title,
                "source": document.source,
                "category": document.category,
                "chunk_id": f"{document.doc_id}-{chunk_index}",
                "path": document.path,
            }
            chunks.append(
                {
                    "id": metadata["chunk_id"],
                    "text": cleaned,
                    "metadata": metadata,
                    "document": asdict(document),
                }
            )

        for units in paragraphs:
            buffer = ""
            for unit in units:
                if len(unit) > self.chunk_size:
                    if buffer:
                        emit(buffer)
                        buffer = ""
                    step = self.chunk_size - self.chunk_overlap or self.chunk_size
                    for start in range(0, len(unit), step):
                        part = unit[start : start + self.chunk_size]
                        emit(part)
                    continue

                candidate = f"{buffer}\n{unit}".strip() if buffer else unit
                if len(candidate) <= self.chunk_size:
                    buffer = candidate
                    continue

                emit(buffer)
                overlap_text = buffer[-self.chunk_overlap :] if self.chunk_overlap and buffer else ""
                buffer = f"{overlap_text}\n{unit}".strip() if overlap_text else unit

            if buffer:
                emit(buffer)
        return chunks
