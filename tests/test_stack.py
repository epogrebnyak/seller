# import pytest  # type: ignore

# from stack import Stack, Batch


# @pytest.fixture
# def s1():
#     return Stack().add(p=90, q=2).add(p=120, q=5).add(p=150, q=3)


# def test_take_last(s1):
#     assert s1.take_last(5) == [Batch(150, 3), Batch(120, 2)]


# def test_take_first(s1):
#     assert s1.take_first(5) == [Batch(90, 2), Batch(120, 3)]


# @pytest.fixture
# def s2(s1):
#     s1.take_first(3)
#     s1.take_last(2)
#     return s1


# def test_take_first_then_last_state(s2):
#     assert s2 == Stack().add(p=120, q=4).add(p=150, q=1)


# def test_take_first_then_last_average(s2):
#     assert s2.average_price == 126.0


# def test_take_first_then_last_quantity(s2):
#     assert s2.quantity == 5
