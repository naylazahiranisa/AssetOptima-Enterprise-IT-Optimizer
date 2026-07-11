"""Recursive character text chunker with configurable size and overlap.

Splits documents into overlapping chunks while preserving metadata.
"""

import logging
import re
from typing import Any

from app.ai.base import Document

logger = logging.getLogger(__name__)


class RecursiveCharacterChunker:
    """Split text into overlapping chunks using recursive separators."""

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200,
                 separators: list[str] | None = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS

    def chunk(self, documents: list[Document]) -> list[Document]:
        """Split each document into overlapping chunks, preserving metadata."""
        chunked = []
        for doc in documents:
            chunks = self._split_text(doc.content)
            for i, chunk_text in enumerate(chunks):
                meta = dict(doc.metadata)
                meta["chunk_index"] = i
                meta["chunk_count"] = len(chunks)
                chunked.append(Document(content=chunk_text, metadata=meta))
        logger.debug("Chunked %d documents into %d chunks", len(documents), len(chunked))
        return chunked

    def _split_text(self, text: str) -> list[str]:
        """Recursively split text by separators until all chunks are within size."""
        if len(text) <= self.chunk_size:
            return [text]
        chunks = []
        for sep in self.separators:
            if sep == "":
                chunks = self._split_by_characters(text)
                break
            chunks = self._split_by_separator(text, sep)
            if all(len(c) <= self.chunk_size for c in chunks):
                break
        return self._merge_with_overlap(chunks)

    def _split_by_separator(self, text: str, separator: str) -> list[str]:
        if separator == "":
            return list(text)
        parts = text.split(separator)
        merged = []
        current = ""
        for part in parts:
            candidate = current + (separator if current else "") + part
            if len(candidate) <= self.chunk_size or not current:
                current = candidate
            else:
                merged.append(current)
                current = part
        if current:
            merged.append(current)
        return merged

    def _split_by_characters(self, text: str) -> list[str]:
        return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

    def _merge_with_overlap(self, chunks: list[str]) -> list[str]:
        if self.chunk_overlap <= 0 or len(chunks) <= 1:
            return chunks
        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = result[-1]
            overlap_start = max(0, len(prev) - self.chunk_overlap)
            overlap_text = prev[overlap_start:]
            result.append(overlap_text + chunks[i])
        return result
