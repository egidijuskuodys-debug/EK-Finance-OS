from pydantic import BaseModel, Field


class MultiFileImportRequest(BaseModel):
    broker: str = Field(
        min_length=2,
        max_length=100,
    )

    file_paths: list[str] = Field(
        min_length=1,
    )