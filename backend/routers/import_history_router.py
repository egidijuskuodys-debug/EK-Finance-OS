from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.import_history_schema import (
    ImportHistoryResponse,
)
from services.import_history_service import (
    get_history,
)


router = APIRouter(
    prefix="/import-history",
    tags=["Import History"],
)


@router.get(
    "/",
    response_model=list[
        ImportHistoryResponse
    ],
)
def list_import_history(
    db: Session = Depends(get_db),
):
    return get_history(db)