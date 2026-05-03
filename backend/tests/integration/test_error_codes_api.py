from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.models.error_code import ErrorCode, Manufacturer
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
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


async def seed_knowledge_manual(db_session) -> KnowledgeDocument:
    now = datetime.now(timezone.utc)
    document = KnowledgeDocument(
        id=uuid4(),
        title="Manual Carrier 38AKS",
        source="Manual PDF Carrier 38AKS",
        doc_type="manual",
        manufacturer="Carrier",
        equipment_model="38AKS",
        category="refrigeration",
        metadata_={"pages": 20},
        chunk_count=1,
        created_at=now,
    )
    db_session.add(document)
    await db_session.flush()

    db_session.add(
        KnowledgeChunk(
            id=uuid4(),
            document_id=document.id,
            content=(
                "Tabla de codigos de error\n"
                "Codigo E7: Sensor de evaporador fuera de rango.\n"
                "Codigo E8 - Proteccion de alta temperatura."
            ),
            chunk_index=0,
            manufacturer=document.manufacturer,
            equipment_model=document.equipment_model,
            category=document.category,
            extra_metadata={"page": 12},
            embedding=None,
            created_at=now,
        )
    )
    await db_session.flush()
    return document


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


@pytest.mark.asyncio
async def test_extract_error_codes_from_knowledge_requires_review_before_search(
    error_codes_app,
    db_session,
):
    document = await seed_knowledge_manual(db_session)

    transport = ASGITransport(app=error_codes_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        extract_response = await client.post(
            f"/error-codes/extract/from-document/{document.id}",
            json={"auto_approve": False},
        )
        default_search = await client.get(
            "/error-codes/",
            params={"query": "E7"},
        )
        pending_search = await client.get(
            "/error-codes/",
            params={"query": "E7", "review_status": "pending_review"},
        )

        pending_body = pending_search.json()
        review_response = await client.patch(
            f"/error-codes/{pending_body[0]['id']}/review",
            json={"review_status": "approved"},
        )
        approved_search = await client.get(
            "/error-codes/",
            params={"query": "E7"},
        )

    assert extract_response.status_code == 200
    extract_body = extract_response.json()
    assert extract_body["created"] == 2
    assert extract_body["status"] == "pending_review"
    assert {item["code"] for item in extract_body["error_codes"]} == {"E7", "E8"}
    assert all(
        item["source_document_id"] == str(document.id)
        for item in extract_body["error_codes"]
    )
    assert all(item["source_page"] == 12 for item in extract_body["error_codes"])

    assert default_search.status_code == 200
    assert default_search.json() == []

    assert pending_search.status_code == 200
    assert [item["code"] for item in pending_body] == ["E7"]

    assert review_response.status_code == 200
    assert review_response.json()["review_status"] == "approved"

    assert approved_search.status_code == 200
    approved_body = approved_search.json()
    assert len(approved_body) == 1
    assert approved_body[0]["code"] == "E7"
    assert approved_body[0]["source"] == "Manual PDF Carrier 38AKS"


@pytest.mark.asyncio
async def test_update_error_code_candidate_before_approval(
    error_codes_app,
    db_session,
):
    document = await seed_knowledge_manual(db_session)

    transport = ASGITransport(app=error_codes_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        extract_response = await client.post(
            f"/error-codes/extract/from-document/{document.id}",
            json={"auto_approve": False},
        )
        candidate = extract_response.json()["error_codes"][0]

        update_response = await client.patch(
            f"/error-codes/{candidate['id']}",
            json={
                "description": "Sensor de evaporador fuera de rango o desconectado.",
                "severity": "High",
                "possible_causes": [
                    "Sensor abierto",
                    "Conector sulfatado",
                    "   ",
                ],
                "suggested_fix": "Medir resistencia del sensor y revisar conectores.",
                "model": "38AKS-RGC",
                "source_page": 13,
                "source_excerpt": "Codigo E7: Sensor de evaporador fuera de rango.",
            },
        )
        review_response = await client.patch(
            f"/error-codes/{candidate['id']}/review",
            json={"review_status": "approved"},
        )
        search_response = await client.get(
            "/error-codes/",
            params={"query": "desconectado", "model": "RGC"},
        )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["description"] == (
        "Sensor de evaporador fuera de rango o desconectado."
    )
    assert updated["severity"] == "high"
    assert updated["possible_causes"] == ["Sensor abierto", "Conector sulfatado"]
    assert updated["suggested_fix"] == (
        "Medir resistencia del sensor y revisar conectores."
    )
    assert updated["model"] == "38AKS-RGC"
    assert updated["source_page"] == 13
    assert updated["review_status"] == "pending_review"

    assert review_response.status_code == 200
    assert review_response.json()["review_status"] == "approved"

    assert search_response.status_code == 200
    body = search_response.json()
    assert len(body) == 1
    assert body[0]["id"] == candidate["id"]


@pytest.mark.asyncio
async def test_update_error_code_rejects_invalid_severity(
    error_codes_app,
    db_session,
):
    await seed_error_codes(db_session)

    transport = ASGITransport(app=error_codes_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        search_response = await client.get(
            "/error-codes/",
            params={"query": "E7"},
        )
        error_code_id = search_response.json()[0]["id"]
        update_response = await client.patch(
            f"/error-codes/{error_code_id}",
            json={"severity": "urgent"},
        )

    assert update_response.status_code == 422
    assert update_response.json()["detail"] == (
        "severity debe ser low, medium, high o critical"
    )
