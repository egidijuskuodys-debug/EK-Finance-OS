from pathlib import Path

from database.db import SessionLocal
from importers.ibkr.section_reader import (
    read_ibkr_file,
)
from importers.ibkr.trades_parser import (
    parse_forex_cash_movements,
)
from services.import_engine.cash_movement_importer import (
    import_cash_movements,
)


def main() -> None:
    db = SessionLocal()

    try:
        backend_dir = Path("/app")

        files = sorted(
            backend_dir.glob(
                "U15039945_*.csv"
            )
        )

        total_parsed = 0
        total_imported = 0
        total_skipped = 0

        print(
            f"IBKR files found: {len(files)}"
        )

        for file_path in files:
            sections, _ = read_ibkr_file(
                str(file_path)
            )

            forex_movements = (
                parse_forex_cash_movements(
                    sections.get(
                        "Trades",
                        [],
                    )
                )
            )

            total_parsed += len(
                forex_movements
            )

            result = import_cash_movements(
                db,
                forex_movements,
            )

            db.commit()

            total_imported += result[
                "imported"
            ]

            total_skipped += result[
                "skipped"
            ]

            print(
                f"{file_path.name}: "
                f"parsed={len(forex_movements)}, "
                f"imported={result['imported']}, "
                f"skipped={result['skipped']}"
            )

        print()
        print(
            f"Total parsed: {total_parsed}"
        )
        print(
            f"Total imported: {total_imported}"
        )
        print(
            f"Total skipped: {total_skipped}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()