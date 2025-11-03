from seller import Item, Sale, Batch, Parcel


def test_item_matmul_and_mul_create_sale():
    item = Item("A")
    s = item @ 2.0 * 3

    assert isinstance(s, Sale)
    assert s.name == "A"
    assert s.price == 2.0
    assert s.quantity == 3
    assert s.revenue == 6.0
    assert s.batch == Batch(2.0, 3)


def test_sale_setters_mutating():
    s = Sale("B", price=0.0, quantity=0)
    s @ 5.5
    s * 2

    assert s.price == 5.5
    assert s.quantity == 2
    assert s.revenue == 11.0


def test_parcel_properties_and_sale_conversion():
    p = Parcel("A", price=10.0)
    p.append(Batch(2.0, 3)).append(Batch(3.0, 1))

    assert p.quantity == 4
    assert p.cogs == 2.0 * 3 + 3.0 * 1

    s = p.sale
    assert isinstance(s, Sale)
    assert (s.name, s.price, s.quantity) == ("A", 10.0, 4)
