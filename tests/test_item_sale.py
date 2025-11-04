from seller import Item, Order, Batch, Parcel


def test_item_matmul_and_mul_create_Order():
    item = Item("A")
    s = item @ 2.0 * 3

    assert isinstance(s, Order)
    assert s.name == "A"
    assert s.price == 2.0
    assert s.quantity == 3
    assert s.worth == 6.0
    assert s.batch == Batch(2.0, 3)


def test_Order_setters_mutating():
    s = Order("B", price=0.0, quantity=0)
    s @ 5.5  # type: ignore
    s * 2  # type: ignore

    assert s.price == 5.5
    assert s.quantity == 2
    assert s.worth == 11.0


def test_parcel_properties_and_Order_conversion():
    p = Parcel("A", price=10.0)
    p.batches.append(Batch(2.0, 3))
    p.batches.append(Batch(3.0, 1))

    assert p.quantity == 4
    assert p.cogs == 2.0 * 3 + 3.0 * 1

    s = p.to_order()
    assert isinstance(s, Order)
    assert (s.name, s.price, s.quantity) == ("A", 10.0, 4)
