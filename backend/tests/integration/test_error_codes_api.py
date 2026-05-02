from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.models.error_code import ErrorCode, Manufacturer
from app.routers.error_codes import router as error_codes_router


pytestmark = pytest.mark.integration


@pytest.fixture
def error_codes_app(db_session):
    app = FastAPI()
    app.include_router(error_codes_router, prefix="/error-codes")

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


async def seed_error_codes(db_session):
    carrier = Manufacturer(
        id=uuid4(),
        name="Carrier",
        country="United States",
        website="https://www.carrier.com",
        created_at=datetime.now(timezone.utc),
    )
    daikin = Manufacturer(
        id=uuid4(),
        name="Daikin",
        country="Japan",
        website="https://www.daikin.com",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add_all([carrier, daikin])
    await db_session.flush()

    now = datetime.now(timezone.utc)
    db_session.add_all(
        [
            ErrorCode(
                id=uuid4(),
                code="E7",
                description="Sensor de evaporador fuera de rango.",
                manufacturer_id=carrier.id,
                manufacturer=carrier.name,
                model="38AKS",
                severity="medium",
                possible_causes=["Sensor abierto", "Cableado suelto"],
                suggested_fix="Medir sensor y revisar conectores.",
                source="Manual de servicio Carrier 38AKS",
                created_at=now,
                updated_at=now,
            ),
            ErrorCode(
                id=uuid4(),
                code="E8",
                description="Proteccion de alta temperatura.",
                manufacturer_id=carrier.id,
                manufacturer=carrier.name,
                model="38AKS",
                severity="high",
                possible_causes=["Filtro sucio"],
                suggested_fix="Revisar flujo de aire.",
                source="Manual de servicio Carrier 38AKS",
                created_at=now,
                updated_at=now,
            ),
            ErrorCode(
                id=uuid4(),
                code="U4",
                description="Error de comunicacion entre unidades.",
                manufacturer_id=daikin.id,
                manufacturer=daikin.name,
                model="VRV",
                severity="medium",
                possible_causes=["Cableado de comunicacion"],
                suggested_fix="Verificar cableado y direccionamiento.",
                source="Manual de servicio Daikin VRV",
                created_at=now,
                updated_at=now,
            ),
        ]
    )
    await db_session.flush()


@pytest.mark.asyncio
async def test_search_error_codes_filters_by_code_manufacturer_and_model(
    error_codes_app,
    db_session,
):
    await seed_error_codes(db_session)

    transport = ASGITransport(app=error_codes_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/error-codes/",
            params={"code": "e7", "manufacturer": "carrier", "model": "38"},
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["code"] == "E7"
    assert body[0]["manufacturer"] == "Carrier"
    assert body[0]["model"] == "38AKS"
    assert body[0]["possible_causes"] == ["Sensor abierto", "Cableado suelto"]
    assert body[0]["source"] == "Manual de servicio Carrier 38AKS"


@pytest.mark.asyncio
async def test_search_error_codes_query_matches_description_and_model(
    error_codes_app,
    db_session,
):
    await seed_error_codes(db_session)

    transport = ASGITransport(app=error_codes_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        description_response = await client.get(
            "/error-codes/",
            params={"query": "comunicacion"},
        )
        model_response = await client.get(
            "/error-codes/",
            params={"query": "38AKS"},
        )

    assert description_response.status_code == 200
    assert [item["code"] for item in description_response.json()] == ["U4"]
    assert model_response.status_code == 200
    assert {item["code"] for item in model_response.json()} == {"E7", "E8"}


@pytest.mark.asyncio
async def test_list_manufacturers_returns_real_counts(error_codes_app, db_session):
    await seed_error_codes(db_session)

    transport = ASGITransport(app=error_codes_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/error-codes/manufacturers")

    assert response.status_code == 200
    counts = {item["name"]: item for item in response.json()}

    assert counts["Carrier"]["error_code_count"] == 2
    assert counts["Carrier"]["model_count"] == 1
    assert counts["Daikin"]["error_code_count"] == 1
    assert counts["Daikin"]["model_count"] == 1
