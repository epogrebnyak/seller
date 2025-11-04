import math
from seller import Seller, Item, Stack, InventoryFIFO


def test_examples_basic_flow():
    i = Seller(0.90 * 25 + 0.75 * 50 + 0.65 * 100)
    t1 = Item("Popcorn")
    t2 = Item("Soda 330 ml")

    i.buy(t1 @ 0.90 * 25)
    i.buy(t1 @ 0.75 * 50)
    i.buy(t2 @ 0.65 * 100)

    assert i.hold == InventoryFIFO(
        {
            "Popcorn": Stack().add(0.9, 25).add(0.75, 50),
            "Soda 330 ml": Stack().add(0.65, 100),
        }
    )

    i.sell(t1 @ 2.50 * 35)
    i.sell(t2 @ 1.25 * 50)

    expected_revenue = (35 * 2.50) + (50 * 1.25)
    assert math.isclose(i.revenue, expected_revenue, rel_tol=1e-9, abs_tol=1e-9)

    expected_cogs = (25 * 0.90 + 10 * 0.75) + (50 * 0.65)
    assert math.isclose(i.cogs, expected_cogs, rel_tol=1e-9, abs_tol=1e-9)

    assert math.isclose(i.gross_margin, 87.5, rel_tol=1e-9, abs_tol=1e-9)
