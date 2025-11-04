import math
from seller import Seller, Item, InventoryFIFO


def test_examples_basic_flow():
    i = Seller(cash=0.90 * 25 + 0.75 * 50 + 0.65 * 100)
    t1 = Item("Popcorn")
    t2 = Item("Soda 330 ml")
    i.buy(t1 @ 0.90 * 25)
    i.buy(t1 @ 0.75 * 50)
    i.buy(t2 @ 0.65 * 100)
    i.sell(t1 @ 2.50 * 35)
    i.sell(t2 @ 1.25 * 50)

    expected_revenue = (35 * 2.50) + (50 * 1.25)
    assert math.isclose(i.revenue, expected_revenue)

    expected_cogs = (25 * 0.90 + 10 * 0.75) + (50 * 0.65)
    assert math.isclose(i.cogs, expected_cogs)
    assert math.isclose(i.gross_margin, 87.5)
