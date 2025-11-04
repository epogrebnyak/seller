from seller import Catalog


def test_catalog_register_code_length_and_presence():
    c = Catalog()
    item = c.register("Pen", n_chars=4)

    assert item.name in c
    assert len(item.name) == 4
    assert c[item.name] == "Pen"

    item2 = c.register("Pencil", n_chars=4)
    assert item2.name in c
    assert item2.name != item.name  # unique code


def test_catalog_register_with_explicit_code_and_duplicate():
    c = Catalog()

    # Explicit, unused code stays
    explicit = c.register("Notebook", code="ABCD", n_chars=4)
    assert explicit.name == "ABCD"
    assert c["ABCD"] == "Notebook"

    # Duplicated code gets replaced by a new one
    dupe = c.register("Marker", code="ABCD", n_chars=4)
    assert dupe.name != "ABCD"
    assert dupe.name in c
    assert c[dupe.name] == "Marker"
