"""
Seed priority manufacturers and trusted error-code records.

Run from backend/:
    python scripts/seed_error_codes.py

The initial catalog intentionally avoids inventing manufacturer codes. Add error
codes here only when they come from a trusted manual, service bulletin, or other
traceable source.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import async_session  # noqa: E402
from app.models.error_code import ErrorCode, Manufacturer  # noqa: E402


PRIORITY_MANUFACTURERS = [
    {"name": "Bitzer", "country": "Germany", "website": "https://www.bitzer.de"},
    {"name": "Carrier", "country": "United States", "website": "https://www.carrier.com"},
    {"name": "Copeland", "country": "United States", "website": "https://www.copeland.com"},
    {"name": "Daikin", "country": "Japan", "website": "https://www.daikin.com"},
    {"name": "Danfoss", "country": "Denmark", "website": "https://www.danfoss.com"},
    {"name": "LG", "country": "South Korea", "website": "https://www.lg.com"},
    {"name": "Samsung", "country": "South Korea", "website": "https://www.samsung.com"},
    {"name": "Trane", "country": "Ireland", "website": "https://www.trane.com"},
]

TRUSTED_ERROR_CODES: list[dict] = []


async def get_or_create_manufacturer(session, data: dict) -> Manufacturer:
    manufacturer = await session.scalar(
        select(Manufacturer).where(Manufacturer.name == data["name"])
    )
    if manufacturer is None:
        manufacturer = Manufacturer(
            id=uuid4(),
            name=data["name"],
            country=data.get("country"),
            website=data.get("website"),
            created_at=datetime.now(timezone.utc),
        )
        session.add(manufacturer)
        await session.flush()
        return manufacturer

    manufacturer.country = data.get("country") or manufacturer.country
    manufacturer.website = data.get("website") or manufacturer.website
    return manufacturer


async def upsert_error_code(
    session,
    manufacturer: Manufacturer,
    data: dict,
) -> ErrorCode:
    error_code = await session.scalar(
        select(ErrorCode).where(
            ErrorCode.manufacturer_id == manufacturer.id,
            ErrorCode.code == data["code"],
            ErrorCode.model == data.get("model"),
        )
    )
    if error_code is None:
        error_code = ErrorCode(
            id=uuid4(),
            manufacturer_id=manufacturer.id,
            manufacturer=manufacturer.name,
            code=data["code"],
            model=data.get("model"),
            description=data["description"],
            severity=data.get("severity"),
            possible_causes=data.get("possible_causes") or [],
            suggested_fix=data.get("suggested_fix"),
            source=data.get("source"),
            review_status="approved",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(error_code)
        return error_code

    error_code.manufacturer = manufacturer.name
    error_code.description = data["description"]
    error_code.severity = data.get("severity")
    error_code.possible_causes = data.get("possible_causes") or []
    error_code.suggested_fix = data.get("suggested_fix")
    error_code.source = data.get("source")
    error_code.review_status = "approved"
    error_code.updated_at = datetime.now(timezone.utc)
    return error_code


async def main() -> None:
    async with async_session() as session:
        manufacturers = {}
        for manufacturer_data in PRIORITY_MANUFACTURERS:
            manufacturer = await get_or_create_manufacturer(session, manufacturer_data)
            manufacturers[manufacturer.name] = manufacturer

        seeded_codes = 0
        for code_data in TRUSTED_ERROR_CODES:
            manufacturer = manufacturers.get(code_data["manufacturer"])
            if manufacturer is None:
                manufacturer = await get_or_create_manufacturer(
                    session,
                    {"name": code_data["manufacturer"]},
                )
                manufacturers[manufacturer.name] = manufacturer
            await upsert_error_code(session, manufacturer, code_data)
            seeded_codes += 1

        await session.commit()

    print(
        "Seed completed: "
        f"{len(manufacturers)} manufacturers, {seeded_codes} trusted error codes."
    )


if __name__ == "__main__":
    asyncio.run(main())
