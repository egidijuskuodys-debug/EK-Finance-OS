from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ImportHistoryResponse(BaseModel):
    id: int
    broker: str
    file_name: str
    file_hash: str
    imported_at: datetime

    transactions_count: int
    dividends_count: int
    cash_movements_count: int
    positions_count: int
    duplicates_skipped: int

    status: str
    error_message: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )