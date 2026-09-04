from sqlalchemy.orm import Session

from models.transaction import Transaction
from models.transaction_lot import TransactionLot
from repositories import (
    investment_repository,
    transaction_lot_repository,
    transaction_repository,
)
from schemas.transaction_schema import TransactionCreate


QUANTITY_EPSILON = 0.0001


def get_transactions(
    db: Session,
):
    return transaction_repository.get_all(db)


def get_transaction_by_id(
    db: Session,
    transaction_id: int,
):
    return transaction_repository.get_by_id(
        db,
        transaction_id,
    )


def clear_transaction_lots(
    db: Session,
    investment_id: int,
):
    db.query(TransactionLot).filter(
        TransactionLot.investment_id
        == investment_id
    ).delete(
        synchronize_session=False,
    )

    db.flush()


def calculate_buy_unit_cost(
    transaction: Transaction,
) -> float:
    if transaction.quantity <= 0:
        raise ValueError(
            "BUY transaction quantity "
            "must be greater than zero."
        )

    commission = (
        transaction.commission
        or 0
    )

    total_cost = (
        transaction.quantity
        * transaction.price
        + commission
    )

    return (
        total_cost
        / transaction.quantity
    )


def calculate_sell_net_unit_price(
    transaction: Transaction,
) -> float:
    if transaction.quantity <= 0:
        raise ValueError(
            "SELL or REDEMPTION transaction "
            "quantity must be greater than zero."
        )

    commission = (
        transaction.commission
        or 0
    )

    net_proceeds = (
        transaction.quantity
        * transaction.price
        - commission
    )

    return (
        net_proceeds
        / transaction.quantity
    )


def normalize_lot_quantity(
    lot: TransactionLot,
) -> None:
    if (
        abs(lot.remaining_quantity)
        < QUANTITY_EPSILON
    ):
        lot.remaining_quantity = 0


def process_sell_transaction(
    transaction: Transaction,
    active_lots: list[TransactionLot],
) -> None:
    available_quantity = sum(
        lot.remaining_quantity
        for lot in active_lots
    )

    if transaction.quantity > (
        available_quantity
        + QUANTITY_EPSILON
    ):
        raise ValueError(
            "Transaction history would "
            "create a negative "
            "investment quantity."
        )

    quantity_to_sell = (
        transaction.quantity
    )

    sell_unit_price = (
        calculate_sell_net_unit_price(
            transaction
        )
    )

    realized_profit = 0.0

    for lot in active_lots:
        if (
            quantity_to_sell
            <= QUANTITY_EPSILON
        ):
            quantity_to_sell = 0
            break

        if (
            lot.remaining_quantity
            <= 0
        ):
            continue

        quantity_from_lot = min(
            quantity_to_sell,
            lot.remaining_quantity,
        )

        realized_profit += (
            sell_unit_price
            - lot.purchase_price
        ) * quantity_from_lot

        lot.remaining_quantity -= (
            quantity_from_lot
        )

        quantity_to_sell -= (
            quantity_from_lot
        )

        normalize_lot_quantity(
            lot
        )

    if (
        quantity_to_sell
        > QUANTITY_EPSILON
    ):
        raise ValueError(
            "Transaction history would "
            "create a negative "
            "investment quantity."
        )

    transaction.realized_profit = round(
        realized_profit,
        2,
    )


def process_quantity_adjustment(
    transaction: Transaction,
    active_lots: list[TransactionLot],
) -> None:
    if transaction.quantity <= 0:
        raise ValueError(
            "QUANTITY_ADJUSTMENT quantity "
            "must be greater than zero."
        )

    active_quantity = sum(
        lot.remaining_quantity
        for lot in active_lots
        if lot.remaining_quantity
        > QUANTITY_EPSILON
    )

    if active_quantity <= QUANTITY_EPSILON:
        raise ValueError(
            "QUANTITY_ADJUSTMENT requires "
            "an existing positive position."
        )

    adjustment_factor = (
        active_quantity
        + transaction.quantity
    ) / active_quantity

    for lot in active_lots:
        if (
            lot.remaining_quantity
            <= QUANTITY_EPSILON
        ):
            continue

        old_remaining_quantity = (
            lot.remaining_quantity
        )

        old_remaining_cost = (
            old_remaining_quantity
            * lot.purchase_price
        )

        adjusted_quantity = (
            old_remaining_quantity
            * adjustment_factor
        )

        quantity_increase = (
            adjusted_quantity
            - old_remaining_quantity
        )

        lot.remaining_quantity = (
            adjusted_quantity
        )

        lot.original_quantity += (
            quantity_increase
        )

        if (
            lot.remaining_quantity
            > QUANTITY_EPSILON
        ):
            lot.purchase_price = (
                old_remaining_cost
                / lot.remaining_quantity
            )

        normalize_lot_quantity(
            lot
        )

    transaction.realized_profit = 0


def recalculate_position(
    db: Session,
    investment_id: int,
):
    investment = (
        investment_repository.get_by_id(
            db,
            investment_id,
        )
    )

    if investment is None:
        raise ValueError(
            "Investment not found."
        )

    transactions = (
        transaction_repository
        .get_by_investment_id(
            db,
            investment_id,
        )
    )

    clear_transaction_lots(
        db,
        investment_id,
    )

    active_lots: list[
        TransactionLot
    ] = []

    for transaction in transactions:
        transaction_type = (
            transaction
            .transaction_type
            .upper()
        )

        if transaction_type == "BUY":
            transaction.realized_profit = 0

            purchase_price = (
                calculate_buy_unit_cost(
                    transaction
                )
            )

            lot = TransactionLot(
                investment_id=investment_id,
                buy_transaction_id=(
                    transaction.id
                ),
                original_quantity=(
                    transaction.quantity
                ),
                remaining_quantity=(
                    transaction.quantity
                ),
                purchase_price=(
                    purchase_price
                ),
                purchase_date=(
                    transaction
                    .transaction_date
                ),
            )

            transaction_lot_repository.create(
                db,
                lot,
            )

            active_lots.append(
                lot
            )

        elif transaction_type in {
            "SELL",
            "REDEMPTION",
        }:
            process_sell_transaction(
                transaction,
                active_lots,
            )

        elif (
            transaction_type
            == "QUANTITY_ADJUSTMENT"
        ):
            process_quantity_adjustment(
                transaction,
                active_lots,
            )

        else:
            raise ValueError(
                "Unsupported transaction type: "
                f"{transaction_type}."
            )

    for lot in active_lots:
        normalize_lot_quantity(
            lot
        )

    remaining_quantity = sum(
        lot.remaining_quantity
        for lot in active_lots
    )

    if (
        abs(remaining_quantity)
        < QUANTITY_EPSILON
    ):
        remaining_quantity = 0

    remaining_cost = sum(
        lot.remaining_quantity
        * lot.purchase_price
        for lot in active_lots
    )

    investment.quantity = round(
        remaining_quantity,
        8,
    )

    if remaining_quantity > 0:
        investment.purchase_price = round(
            remaining_cost
            / remaining_quantity,
            8,
        )
    else:
        investment.purchase_price = 0

    db.flush()

    return investment


def create_transaction(
    db: Session,
    transaction_data: TransactionCreate,
):
    investment = (
        investment_repository.get_by_id(
            db,
            transaction_data.investment_id,
        )
    )

    if investment is None:
        raise ValueError(
            "Investment not found."
        )

    if (
        transaction_data.currency
        != investment.currency
    ):
        raise ValueError(
            "Transaction currency must "
            "match investment currency."
        )

    if (
        transaction_data
        .broker_transaction_id
    ):
        duplicate_exists = (
            transaction_repository
            .exists_by_broker_transaction_id(
                db,
                transaction_data
                .broker_transaction_id,
            )
        )

        if duplicate_exists:
            raise ValueError(
                "Transaction has already "
                "been imported."
            )

    transaction_type = (
        transaction_data
        .transaction_type
        .upper()
    )

    commission = getattr(
        transaction_data,
        "commission",
        0,
    )

    if commission is None:
        commission = 0

    commission = float(
        commission
    )

    if commission < 0:
        raise ValueError(
            "Transaction commission "
            "cannot be negative."
        )

    try:
        new_transaction = Transaction(
            investment_id=(
                transaction_data
                .investment_id
            ),
            broker_transaction_id=(
                transaction_data
                .broker_transaction_id
            ),
            transaction_type=(
                transaction_type
            ),
            quantity=(
                transaction_data.quantity
            ),
            price=(
                transaction_data.price
            ),
            commission=commission,
            realized_profit=0,
            currency=(
                transaction_data.currency
            ),
            transaction_date=(
                transaction_data
                .transaction_date
            ),
        )

        transaction_repository.add(
            db,
            new_transaction,
        )

        recalculate_position(
            db,
            transaction_data.investment_id,
        )

        db.commit()

        db.refresh(
            new_transaction
        )

        db.refresh(
            investment
        )

        return new_transaction

    except Exception:
        db.rollback()
        raise


def delete_transaction(
    db: Session,
    transaction_id: int,
):
    transaction = (
        transaction_repository.get_by_id(
            db,
            transaction_id,
        )
    )

    if transaction is None:
        return None

    investment_id = (
        transaction.investment_id
    )

    try:
        clear_transaction_lots(
            db,
            investment_id,
        )

        transaction_repository.delete(
            db,
            transaction,
        )

        recalculate_position(
            db,
            investment_id,
        )

        db.commit()

        return {
            "message": (
                "Transaction deleted "
                "successfully"
            )
        }

    except Exception:
        db.rollback()
        raise