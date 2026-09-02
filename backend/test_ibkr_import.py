from pprint import pprint

from importers.factory import ImporterFactory


CSV_FILE_PATH = "/app/U15039945_202607_202607.csv"


def main():
    importer = ImporterFactory.get_importer(
        broker="IBKR",
        file_path=CSV_FILE_PATH,
    )

    preview = importer.preview()

    print("\n=== IBKR IMPORT PREVIEW ===\n")

    print(
        f"Broker: {preview['broker']}"
    )

    print(
        f"File: {preview['file_name']}"
    )

    print(
        f"Transactions: "
        f"{preview['transactions_count']}"
    )

    print(
        f"Dividends: "
        f"{preview['dividends_count']}"
    )

    print(
        f"Cash movements: "
        f"{preview['cash_movements_count']}"
    )

    print(
        f"Positions: "
        f"{preview['positions_count']}"
    )

    print(
        f"Fees: "
        f"{preview['fees_count']}"
    )

    print("\nDetected sections:")

    for section in preview[
        "detected_sections"
    ]:
        print(
            f"- {section}"
        )

    print("\nFirst parsed transaction:")

    transactions = preview[
        "data"
    ].get(
        "transactions",
        [],
    )

    if transactions:
        pprint(
            transactions[0]
        )
    else:
        print(
            "No transactions found."
        )

    print("\nFirst parsed dividend:")

    dividends = preview[
        "data"
    ].get(
        "dividends",
        [],
    )

    if dividends:
        pprint(
            dividends[0]
        )
    else:
        print(
            "No dividends found."
        )

    print("\nFirst parsed cash movement:")

    cash_movements = preview[
        "data"
    ].get(
        "cash_movements",
        [],
    )

    if cash_movements:
        pprint(
            cash_movements[0]
        )
    else:
        print(
            "No cash movements found."
        )

    print("\nFirst parsed position:")

    positions = preview[
        "data"
    ].get(
        "positions",
        [],
    )

    if positions:
        pprint(
            positions[0]
        )
    else:
        print(
            "No positions found."
        )


if __name__ == "__main__":
    main()