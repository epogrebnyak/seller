import math
import pytest  # type: ignore

from seller import (
    Seller,
    Item,
    Batch,
    Order,
    NotInStock,
    InsufficientStock,
    InsufficientFunds,
)


def test_buy():
    i = Seller(0.5 * 10 + 0.6 * 5)
    pen = Item("Pen")
    i.buy(pen @ 0.5 * 10)
    i.buy(pen @ 0.6 * 5)

    assert i.hold["Pen"][0] == Batch(0.5, 10)
    assert i.hold["Pen"][1] == Batch(0.6, 5)
    assert i.hold["Pen"].quantity == 15


def test_sell_fifo_partial_batches():
    i = Seller(0.5 * 10 + 0.6 * 10)
    pen = Item("Pen")
    i.buy(pen @ 0.5 * 10)
    i.buy(pen @ 0.6 * 10)

    i.sell(pen @ 1.0 * 15)

    # One fulfillment recorded
    assert len(i.fulfilled) == 1

    # Remaining inventory is 5 units @ 0.6
    assert i.hold["Pen"][0] == Batch(0.6, 5)

    # Revenue and COGS
    assert math.isclose(i.revenue, 15.0)
    assert math.isclose(i.cogs, 10 * 0.5 + 5 * 0.6)
    assert math.isclose(i.gross_margin, 15.0 - (10 * 0.5 + 5 * 0.6))
    assert math.isclose(i.earned, i.gross_margin)

    # Sales object derived from parcel
    sales = i.sales
    assert len(sales) == 1
    s = sales[0]
    assert isinstance(s, Order)
    assert s.name == "Pen" and s.price == 1.0 and s.quantity == 15


def test_sell_insufficient_cash():
    i = Seller(0)
    pen = Item("Pen")
    with pytest.raises(InsufficientFunds):
        i.buy(pen @ 0.5 * 5)


def test_sell_insufficient_stock_noop():
    i = Seller(2.5)
    pen = Item("Pen")
    i.buy(pen @ 0.5 * 5)
    with pytest.raises(InsufficientStock):
        i.sell(pen @ 1.0 * 6)


def test_sell_unknown_item():
    i = Seller()
    with pytest.raises(NotInStock):
        i.sell(Item("Ghost") @ 1.0 * 1)


def test_expenses_and_earned():
    i = Seller(cash=0.5 * 10 + 0.6 * 10)
    pen = Item("Pen")
    i.buy(pen @ 0.5 * 10).sell(pen @ 1.0 * 10).pay(2.0, "fee")
    assert math.isclose(i.expenses, 2.0)
    assert math.isclose(i.earned, i.gross_margin - 2.0)


def test_multiple_sales_accumulate():
    i = Seller(cash=0.5 * 10 + 0.6 * 10)
    pen = Item("Pen")
    i.buy(pen @ 0.5 * 10)
    i.buy(pen @ 0.6 * 10)

    i.sell(pen @ 1.0 * 12)
    i.sell(pen @ 1.2 * 6)

    # After first sell (12): remaining  - 0.5(0), 0.6(8)
    # After second sell (6): take 6 from 0.6 -> remaining 0.6(2)
    assert i.hold["Pen"][0] == Batch(0.6, 2)

    # Revenue
    assert math.isclose(i.revenue, 12 * 1.0 + 6 * 1.2)

    # COGS: first: 10*0.5 + 2*0.6, second: 6*0.6
    assert math.isclose(i.cogs, 10 * 0.5 + 8 * 0.6)
