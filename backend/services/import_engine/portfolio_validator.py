from typing import Any

from sqlalchemy.orm import Session

from repositories import investment_repository


QUANTITY_TOLERANCE = 0.000001
PRICE_TOLERANCE = 0.01


def numbers_match(
    first: float,
    second: float,
    tolerance: float,
) -> bool:
    return abs(first - second) <= tolerance


def validate_portfolio(
    db: Session,
    broker: str,
    ibkr_positions: list[dict[str, Any]],
) -> dict[str, Any]:
    database_investments = (
        investment_repository.get_all(db)
    )

    database_positions = {
        investment.ticker: investment
        for investment in database_investments
        if investment.broker == broker
        and investment.quantity > 0
    }

    ibkr_position_lookup = {
        position["ticker"]: position
        for position in ibkr_positions
    }

    results = []

    matched = 0
    mismatched = 0
    missing_in_database = 0
    extra_in_database = 0

    quantity_mismatches = 0
    currency_mismatches = 0
    cost_price_differences = 0

    for ticker, ibkr_position in (
        ibkr_position_lookup.items()
    ):
        investment = database_positions.get(
            ticker
        )

        if investment is None:
            missing_in_database += 1
            mismatched += 1

            results.append(
                {
                    "ticker": ticker,
                    "status": "MISSING_IN_DATABASE",
                    "quantity": {
                        "match": False,
                        "ibkr": ibkr_position[
                            "quantity"
                        ],
                        "database": None,
                        "difference": None,
                    },
                    "currency": {
                        "match": False,
                        "ibkr": ibkr_position[
                            "currency"
                        ],
                        "database": None,
                    },
                    "purchase_price": {
                        "status": "INFO_ONLY",
                        "ibkr": round(
                            ibkr_position[
                                "purchase_price"
                            ],
                            8,
                        ),
                        "database": None,
                        "difference": None,
                    },
                }
            )

            continue

        quantity_match = numbers_match(
            investment.quantity,
            ibkr_position["quantity"],
            QUANTITY_TOLERANCE,
        )

        currency_match = (
            investment.currency
            == ibkr_position["currency"]
        )

        if not quantity_match:
            quantity_mismatches += 1

        if not currency_match:
            currency_mismatches += 1

        position_matches = (
            quantity_match
            and currency_match
        )

        if position_matches:
            matched += 1
            status = "MATCH"
        else:
            mismatched += 1
            status = "MISMATCH"

        purchase_price_difference = round(
            investment.purchase_price
            - ibkr_position[
                "purchase_price"
            ],
            8,
        )

        purchase_price_close = numbers_match(
            investment.purchase_price,
            ibkr_position[
                "purchase_price"
            ],
            PRICE_TOLERANCE,
        )

        if not purchase_price_close:
            cost_price_differences += 1

        results.append(
            {
                "ticker": ticker,
                "status": status,
                "quantity": {
                    "match": quantity_match,
                    "ibkr": ibkr_position[
                        "quantity"
                    ],
                    "database": (
                        investment.quantity
                    ),
                    "difference": round(
                        investment.quantity
                        - ibkr_position[
                            "quantity"
                        ],
                        8,
                    ),
                },
                "currency": {
                    "match": currency_match,
                    "ibkr": ibkr_position[
                        "currency"
                    ],
                    "database": (
                        investment.currency
                    ),
                },
                "purchase_price": {
                    "status": "INFO_ONLY",
                    "within_tolerance": (
                        purchase_price_close
                    ),
                    "ibkr": round(
                        ibkr_position[
                            "purchase_price"
                        ],
                        8,
                    ),
                    "database": round(
                        investment.purchase_price,
                        8,
                    ),
                    "difference": (
                        purchase_price_difference
                    ),
                },
            }
        )

    for ticker, investment in (
        database_positions.items()
    ):
        if ticker in ibkr_position_lookup:
            continue

        extra_in_database += 1
        mismatched += 1

        results.append(
            {
                "ticker": ticker,
                "status": "EXTRA_IN_DATABASE",
                "quantity": {
                    "match": False,
                    "ibkr": None,
                    "database": (
                        investment.quantity
                    ),
                    "difference": None,
                },
                "currency": {
                    "match": False,
                    "ibkr": None,
                    "database": (
                        investment.currency
                    ),
                },
                "purchase_price": {
                    "status": "INFO_ONLY",
                    "ibkr": None,
                    "database": round(
                        investment.purchase_price,
                        8,
                    ),
                    "difference": None,
                },
            }
        )

    portfolio_matches = (
        mismatched == 0
    )

    return {
        "portfolio_matches": (
            portfolio_matches
        ),
        "broker": broker,
        "summary": {
            "ibkr_positions": len(
                ibkr_positions
            ),
            "database_positions": len(
                database_positions
            ),
            "matched": matched,
            "mismatched": mismatched,
            "missing_in_database": (
                missing_in_database
            ),
            "extra_in_database": (
                extra_in_database
            ),
            "quantity_mismatches": (
                quantity_mismatches
            ),
            "currency_mismatches": (
                currency_mismatches
            ),
            "cost_price_differences": (
                cost_price_differences
            ),
        },
        "validation_rules": {
            "ticker": "REQUIRED",
            "quantity": "REQUIRED",
            "currency": "REQUIRED",
            "purchase_price": "INFORMATIONAL",
        },
        "results": results,
    }