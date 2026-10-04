from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.db import Base
from models.investment import Investment
from models.transaction import Transaction
from models.transaction_lot import TransactionLot
from schemas.transaction_schema import TransactionCreate
from services.transaction_service import (
    create_transaction,
    delete_transaction,
)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(
        bind=engine,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(
            bind=engine,
        )


@pytest.fixture()
def investment(db):
    item = Investment(
        broker="Interactive Brokers",
        asset="Vanguard FTSE All-World",
        ticker="VWCE",
        market_ticker="VWCE.DE",
        asset_type="ETF",
        quantity=0,
        purchase_price=0,
        current_price=100,
        currency="EUR",
        purchase_date=date(
            2026,
            1,
            1,
        ),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def make_transaction(
    investment_id: int,
    transaction_type: str,
    quantity: float,
    price: float,
    transaction_date: date,
    commission: float = 0,
):
    return TransactionCreate(
        investment_id=investment_id,
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        commission=commission,
        currency="EUR",
        transaction_date=transaction_date,
    )


def test_buy_creates_position(
    db,
    investment,
):
    transaction = create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    db.refresh(investment)

    assert transaction.transaction_type == "BUY"
    assert investment.quantity == pytest.approx(
        10
    )
    assert investment.purchase_price == pytest.approx(
        100
    )


def test_multiple_buys_calculate_average_cost(
    db,
    investment,
):
    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            120,
            date(
                2026,
                1,
                20,
            ),
        ),
    )

    db.refresh(investment)

    assert investment.quantity == pytest.approx(
        20
    )
    assert investment.purchase_price == pytest.approx(
        110
    )


def test_buy_commission_is_included_in_cost_basis(
    db,
    investment,
):
    transaction = create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
            commission=10,
        ),
    )

    db.refresh(investment)

    assert transaction.commission == pytest.approx(
        10
    )

    assert investment.quantity == pytest.approx(
        10
    )

    assert investment.purchase_price == pytest.approx(
        101
    )


def test_sell_uses_fifo_and_calculates_realized_profit(
    db,
    investment,
):
    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            120,
            date(
                2026,
                1,
                20,
            ),
        ),
    )

    sell = create_transaction(
        db,
        make_transaction(
            investment.id,
            "SELL",
            15,
            130,
            date(
                2026,
                2,
                1,
            ),
        ),
    )

    db.refresh(investment)

    expected_profit = (
        10 * (130 - 100)
        + 5 * (130 - 120)
    )

    assert sell.realized_profit == pytest.approx(
        expected_profit
    )

    assert investment.quantity == pytest.approx(
        5
    )

    assert investment.purchase_price == pytest.approx(
        120
    )


def test_sell_commission_reduces_realized_profit(
    db,
    investment,
):
    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    sell = create_transaction(
        db,
        make_transaction(
            investment.id,
            "SELL",
            10,
            120,
            date(
                2026,
                2,
                1,
            ),
            commission=10,
        ),
    )

    db.refresh(investment)

    assert sell.commission == pytest.approx(
        10
    )

    assert sell.realized_profit == pytest.approx(
        190
    )

    assert investment.quantity == pytest.approx(
        0
    )

    assert investment.purchase_price == pytest.approx(
        0
    )


def test_negative_commission_is_rejected(
    investment,
):
    with pytest.raises(
        ValidationError,
    ):
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
            commission=-1,
        )


def test_cannot_sell_more_than_owned(
    db,
    investment,
):
    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            5,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="negative investment quantity",
    ):
        create_transaction(
            db,
            make_transaction(
                investment.id,
                "SELL",
                6,
                120,
                date(
                    2026,
                    1,
                    20,
                ),
            ),
        )

    db.refresh(investment)

    assert investment.quantity == pytest.approx(
        5
    )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.investment_id
            == investment.id
        )
        .all()
    )

    assert len(transactions) == 1


def test_delete_transaction_recalculates_position(
    db,
    investment,
):
    first_buy = create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    second_buy = create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            120,
            date(
                2026,
                1,
                20,
            ),
        ),
    )

    delete_transaction(
        db,
        second_buy.id,
    )

    db.refresh(investment)

    assert investment.quantity == pytest.approx(
        10
    )

    assert investment.purchase_price == pytest.approx(
        100
    )

    remaining_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.investment_id
            == investment.id
        )
        .all()
    )

    assert len(remaining_transactions) == 1
    assert remaining_transactions[0].id == first_buy.id


def test_quantity_adjustment_preserves_total_cost(
    db,
    investment,
):
    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    create_transaction(
        db,
        make_transaction(
            investment.id,
            "QUANTITY_ADJUSTMENT",
            10,
            0,
            date(
                2026,
                2,
                1,
            ),
        ),
    )

    db.refresh(investment)

    assert investment.quantity == pytest.approx(
        20
    )

    assert investment.purchase_price == pytest.approx(
        50
    )

    assert (
        investment.quantity
        * investment.purchase_price
    ) == pytest.approx(
        1000
    )


def test_transaction_lots_match_remaining_position(
    db,
    investment,
):
    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            100,
            date(
                2026,
                1,
                10,
            ),
        ),
    )

    create_transaction(
        db,
        make_transaction(
            investment.id,
            "BUY",
            10,
            120,
            date(
                2026,
                1,
                20,
            ),
        ),
    )

    create_transaction(
        db,
        make_transaction(
            investment.id,
            "SELL",
            15,
            130,
            date(
                2026,
                2,
                1,
            ),
        ),
    )

    lots = (
        db.query(TransactionLot)
        .filter(
            TransactionLot.investment_id
            == investment.id
        )
        .order_by(
            TransactionLot.purchase_date,
            TransactionLot.id,
        )
        .all()
    )

    remaining_quantity = sum(
        lot.remaining_quantity
        for lot in lots
    )

    assert remaining_quantity == pytest.approx(
        5
    )

    assert investment.quantity == pytest.approx(
        remaining_quantity
    )