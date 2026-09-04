import subprocess
import tempfile
from pathlib import Path

import pymupdf


OCR_LANGUAGES = "lit+eng"
OCR_SCALE = 2.5


def read_seb_pdf_ocr(
    file_path: Path,
) -> list[str]:
    try:
        document = pymupdf.open(
            str(file_path)
        )
    except Exception as exc:
        raise ValueError(
            "Unable to open SEB PDF "
            "for OCR."
        ) from exc

    if document.page_count == 0:
        document.close()

        raise ValueError(
            "SEB PDF does not contain "
            "any pages."
        )

    pages: list[str] = []

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for page_number in range(
                document.page_count
            ):
                page = document[
                    page_number
                ]

                image_path = (
                    temp_path
                    / f"page_{page_number + 1}.png"
                )

                matrix = pymupdf.Matrix(
                    OCR_SCALE,
                    OCR_SCALE,
                )

                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                pixmap.save(
                    str(image_path)
                )

                command = [
                    "tesseract",
                    str(image_path),
                    "stdout",
                    "-l",
                    OCR_LANGUAGES,
                    "--psm",
                    "4",
                ]

                try:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except FileNotFoundError as exc:
                    raise ValueError(
                        "Tesseract OCR is not "
                        "installed."
                    ) from exc
                except subprocess.CalledProcessError as exc:
                    error_message = (
                        exc.stderr.strip()
                        or "Unknown OCR error."
                    )

                    raise ValueError(
                        "Unable to OCR SEB PDF "
                        f"page {page_number + 1}: "
                        f"{error_message}"
                    ) from exc

                text = result.stdout.strip()

                if not text:
                    raise ValueError(
                        "SEB PDF page "
                        f"{page_number + 1} "
                        "does not contain "
                        "readable OCR text."
                    )

                pages.append(
                    text
                )
    finally:
        document.close()

    return pages