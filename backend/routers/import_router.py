import os
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from database.db import get_db
from importers.factory import ImporterFactory
from schemas.multi_import_schema import (
    MultiFileImportRequest,
)
from services.import_engine.multi_file_importer import (
    import_multiple_files,
    preview_multiple_files,
)
from services.import_engine.portfolio_validator import (
    validate_portfolio,
)
from services.import_service import (
    import_file,
    preview_import,
    validate_import,
)


router = APIRouter(
    prefix="/import",
    tags=["Import"],
)


def save_upload_to_temp(
    upload: UploadFile,
) -> str:
    original_name = (
        upload.filename
        or "statement.csv"
    )

    suffix = Path(
        original_name
    ).suffix

    if not suffix:
        suffix = ".csv"

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    try:
        while True:
            chunk = upload.file.read(
                1024 * 1024
            )

            if not chunk:
                break

            temp_file.write(chunk)

    finally:
        temp_file.close()

    return temp_file.name


def remove_temp_file(
    file_path: str,
) -> None:
    try:
        os.remove(file_path)

    except FileNotFoundError:
        pass


@router.post("/preview")
def import_preview(
    broker: str,
    file_path: str,
    db: Session = Depends(get_db),
):
    try:
        return preview_import(
            db=db,
            broker=broker,
            file_path=file_path,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post("/validate")
def validate(
    broker: str,
    file_path: str,
    db: Session = Depends(get_db),
):
    try:
        return validate_import(
            db=db,
            broker=broker,
            file_path=file_path,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post("/import")
def execute_import(
    broker: str,
    file_path: str,
    db: Session = Depends(get_db),
):
    try:
        return import_file(
            db=db,
            broker=broker,
            file_path=file_path,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@router.post("/upload-preview")
def upload_preview(
    broker: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = save_upload_to_temp(
        file
    )

    try:
        preview = preview_import(
            db=db,
            broker=broker,
            file_path=file_path,
        )

        preview["uploaded_file_name"] = (
            file.filename
        )

        return preview

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    finally:
        remove_temp_file(
            file_path
        )


@router.post("/upload-validate")
def upload_validate(
    broker: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = save_upload_to_temp(
        file
    )

    try:
        result = validate_import(
            db=db,
            broker=broker,
            file_path=file_path,
        )

        result["uploaded_file_name"] = (
            file.filename
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    finally:
        remove_temp_file(
            file_path
        )


@router.post("/upload-import")
def upload_import(
    broker: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = save_upload_to_temp(
        file
    )

    try:
        result = import_file(
            db=db,
            broker=broker,
            file_path=file_path,
            original_file_name=(
                file.filename
            ),
        )

        result["uploaded_file_name"] = (
            file.filename
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    finally:
        remove_temp_file(
            file_path
        )


@router.post("/preview-multiple")
def preview_multiple(
    request: MultiFileImportRequest,
):
    try:
        return preview_multiple_files(
            broker=request.broker,
            file_paths=request.file_paths,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post("/import-multiple")
def execute_multiple_import(
    request: MultiFileImportRequest,
    db: Session = Depends(get_db),
):
    try:
        return import_multiple_files(
            db=db,
            broker=request.broker,
            file_paths=request.file_paths,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@router.post("/validate-portfolio")
def validate_imported_portfolio(
    broker: str,
    file_path: str,
    db: Session = Depends(get_db),
):
    try:
        importer = ImporterFactory.get_importer(
            broker=broker,
            file_path=file_path,
        )

        context = importer.build_context()

        return validate_portfolio(
            db=db,
            broker=context.broker,
            ibkr_positions=context.positions,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error