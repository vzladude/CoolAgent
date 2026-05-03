"""
Extract structured error-code candidates from RAG knowledge documents.

Knowledge documents remain the source of truth. Error-code rows are a reviewed
index derived from those documents so mobile search can be fast and traceable.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_code import ErrorCode, Manufacturer
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument


UNKNOWN_MANUFACTURER = "Sin fabricante"
VALID_REVIEW_STATUSES = {"pending_review", "approved", "rejected"}


_CODE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z]{1,3}[\s-]?\d{1,3}[A-Za-z]?)(?![A-Za-z0-9])"
)
_CONTEXT_PATTERN = re.compile(
    r"\b(c[o\u00f3]digo|error|falla|fallo|alarma|fault|alarm|trouble|diagn[o\u00f3]stico)\b",
    re.IGNORECASE,
)
_SKIP_CODE_PATTERN = re.compile(
    r"^(R-?\d|V\d|VAC|DC|AC|HZ|\d+V|R\d)", re.IGNORECASE
)


@dataclass(slots=True)
class ErrorCodeCandidate:
    code: str
    description: str
    source_chunk: KnowledgeChunk
    source_excerpt: str
    confidence: float


class ErrorCodeExtractionService:
    """Build pending error-code records from documents already in knowledge."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_from_document(
        self,
        document_id: uuid.UUID,
        *,
        auto_approve: bool = False,
        max_codes: int = 100,
    ) -> tuple[list[ErrorCode], int]:
        document = await self.db.get(KnowledgeDocument, document_id)
        if document is None:
            raise ValueError("Documento no encontrado")

        result = await self.db.execute(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.document_id == document.id)
            .order_by(KnowledgeChunk.chunk_index.asc())
        )
        chunks = result.scalars().all()

        candidates = self._extract_candidates(chunks, max_codes=max_codes)
        manufacturer = await self._get_or_create_manufacturer(
            document.manufacturer or UNKNOWN_MANUFACTURER
        )

        created: list[ErrorCode] = []
        skipped_existing = 0
        seen_keys: set[tuple[str, str, str | None, uuid.UUID]] = set()
        now = datetime.now(timezone.utc)
        review_status = "approved" if auto_approve else "pending_review"

        for candidate in candidates:
            key = (
                candidate.code,
                manufacturer.name.lower(),
                document.equipment_model.lower() if document.equipment_model else None,
                document.id,
            )
            if key in seen_keys:
                skipped_existing += 1
                continue
            seen_keys.add(key)

            exists = await self._existing_error_code(
                code=candidate.code,
                manufacturer=manufacturer.name,
                model=document.equipment_model,
                source_document_id=document.id,
            )
            if exists is not None:
                skipped_existing += 1
                continue

            error_code = ErrorCode(
                id=uuid.uuid4(),
                code=candidate.code,
                description=candidate.description,
                manufacturer_id=manufacturer.id,
                manufacturer=manufacturer.name,
                model=document.equipment_model,
                severity=None,
                possible_causes=[],
                suggested_fix=None,
                source=document.source or document.title,
                source_document_id=document.id,
                source_chunk_id=candidate.source_chunk.id,
                source_page=self._source_page(candidate.source_chunk),
                source_excerpt=candidate.source_excerpt,
                review_status=review_status,
                confidence=candidate.confidence,
                extraction_metadata={
                    "method": "regex_v1",
                    "document_title": document.title,
                    "chunk_index": candidate.source_chunk.chunk_index,
                    "requires_review": not auto_approve,
                },
                created_at=now,
                updated_at=now,
            )
            self.db.add(error_code)
            created.append(error_code)

        await self.db.flush()
        return created, skipped_existing

    @classmethod
    def _extract_candidates(
        cls,
        chunks: list[KnowledgeChunk],
        *,
        max_codes: int,
    ) -> list[ErrorCodeCandidate]:
        candidates: list[ErrorCodeCandidate] = []
        for chunk in chunks:
            for line_index, line in enumerate(cls._meaningful_lines(chunk.content)):
                for match in _CODE_PATTERN.finditer(line):
                    code = cls._normalize_code(match.group(1))
                    if not cls._looks_like_error_code(code, line):
                        continue

                    description = cls._description_from_line(line, match.end())
                    if not description:
                        description = cls._nearby_description(
                            cls._meaningful_lines(chunk.content),
                            line_index,
                        )
                    if not description:
                        continue

                    excerpt = cls._excerpt(chunk.content, line)
                    candidates.append(
                        ErrorCodeCandidate(
                            code=code,
                            description=description,
                            source_chunk=chunk,
                            source_excerpt=excerpt,
                            confidence=cls._confidence(line, description),
                        )
                    )
                    if len(candidates) >= max_codes:
                        return candidates
        return candidates

    @staticmethod
    def _meaningful_lines(content: str) -> list[str]:
        return [line.strip() for line in content.splitlines() if line.strip()]

    @staticmethod
    def _normalize_code(value: str) -> str:
        return re.sub(r"[\s-]+", "", value).upper()

    @classmethod
    def _looks_like_error_code(cls, code: str, line: str) -> bool:
        if len(code) < 2 or len(code) > 8:
            return False
        if _SKIP_CODE_PATTERN.match(code):
            return False
        if not re.search(r"[A-Z]", code) or not re.search(r"\d", code):
            return False

        line_has_context = _CONTEXT_PATTERN.search(line) is not None
        line_has_delimiter = re.search(r"[:|;=-]", line) is not None
        short_table_row = len(line) <= 180 and line_has_delimiter
        return line_has_context or short_table_row

    @staticmethod
    def _description_from_line(line: str, code_end_index: int) -> str:
        tail = line[code_end_index:].strip(" \t:-\u2013\u2014|;")
        return ErrorCodeExtractionService._clean_description(tail)

    @staticmethod
    def _nearby_description(lines: list[str], line_index: int) -> str:
        for next_line in lines[line_index + 1 : line_index + 3]:
            description = ErrorCodeExtractionService._clean_description(next_line)
            if description:
                return description
        return ""

    @staticmethod
    def _clean_description(value: str) -> str:
        cleaned = re.sub(r"\s+", " ", value).strip(" .:-\u2013\u2014|;")
        if len(cleaned) < 6:
            return ""
        return cleaned[:500]

    @staticmethod
    def _excerpt(content: str, line: str) -> str:
        index = content.find(line)
        if index < 0:
            return content[:700].strip()
        start = max(0, index - 180)
        end = min(len(content), index + len(line) + 360)
        return content[start:end].strip()

    @staticmethod
    def _confidence(line: str, description: str) -> float:
        score = 0.55
        if _CONTEXT_PATTERN.search(line):
            score += 0.2
        if re.search(r"[:|;=-]", line):
            score += 0.1
        if len(description) >= 20:
            score += 0.1
        return min(score, 0.95)

    @staticmethod
    def _source_page(chunk: KnowledgeChunk) -> int | None:
        metadata = chunk.extra_metadata or {}
        page = metadata.get("page") or metadata.get("page_number")
        return page if isinstance(page, int) else None

    async def _get_or_create_manufacturer(self, name: str) -> Manufacturer:
        clean_name = name.strip() or UNKNOWN_MANUFACTURER
        manufacturer = await self.db.scalar(
            select(Manufacturer).where(Manufacturer.name.ilike(clean_name))
        )
        if manufacturer is not None:
            return manufacturer

        manufacturer = Manufacturer(
            id=uuid.uuid4(),
            name=clean_name,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(manufacturer)
        await self.db.flush()
        return manufacturer

    async def _existing_error_code(
        self,
        *,
        code: str,
        manufacturer: str,
        model: str | None,
        source_document_id: uuid.UUID,
    ) -> ErrorCode | None:
        query = (
            select(ErrorCode)
            .where(ErrorCode.code == code)
            .where(ErrorCode.manufacturer.ilike(manufacturer))
            .where(ErrorCode.source_document_id == source_document_id)
        )
        if model:
            query = query.where(ErrorCode.model.ilike(model))
        else:
            query = query.where(ErrorCode.model.is_(None))
        return await self.db.scalar(query)


def validate_review_status(review_status: str) -> str:
    normalized = review_status.strip().lower()
    if normalized not in VALID_REVIEW_STATUSES:
        raise ValueError(
            "review_status debe ser pending_review, approved o rejected"
        )
    return normalized
