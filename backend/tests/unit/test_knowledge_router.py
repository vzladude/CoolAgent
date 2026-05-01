from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.routers.knowledge import upload_pdf


@pytest.mark.asyncio
async def test_upload_pdf_rejects_non_pdf_extension():
    upload = UploadFile(filename="manual.txt", file=BytesIO(b"texto"))

    with pytest.raises(HTTPException) as exc:
        await upload_pdf(file=upload, title="Manual", db=None)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Solo se aceptan archivos PDF"
